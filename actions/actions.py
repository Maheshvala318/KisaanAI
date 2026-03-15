# actions/actions.py
"""
Unified Advanced Action Server for KisaanAI.
Handles text and image-based agricultural disease queries with multilingual support.
Logic flow: Detection -> Retrieval (CSV/RAG) -> Localization -> Response.
"""

import logging
import textwrap
import re
from typing import List, Dict, Any, Optional, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Modular imports
from . import rag
from . import csv_lookup
from .config import disease_data
from .csv_lookup import find_disease_smart, get_info_from_csv, get_canonical_disease_name
from .translation import translate_to_english
from .language_utils import detect_language
from .llm_provider import generate_text

logger = logging.getLogger(__name__)

# ----- Localized labels -----
LANG_LABELS = {
    "gu": {
        "greet": "નમસ્તે ખેડૂત ભાઈ,",
        "no_info": "માફ કરશો, આ રોગ વિશે પૂરતી માહિતી ઉપલબ્ધ નથી.",
        "not_found": "તમારા છોડમાં **{label}** હોવાનું જણાય છે, પણ વિગતવાર માહિતી ગેરહાજર છે.",
        "affected_crops": "આ રોગથી પ્રભાવિત સામાન્ય પાક:",
        "follow_up": "શું તમારે સારવાર અથવા નિવારણની વિગતો જોઈએ છે? (હા/ના)"
    },
    "hi": {
        "greet": "नमस्ते किसान भाई,",
        "no_info": "माफ़ कीजिए, इस रोग की जानकारी उपलब्ध नहीं है।",
        "not_found": "आपके पौधे में **{label}** दिख रहा है, लेकिन अभी इसकी विस्तृत जानकारी उपलब्ध नहीं है।",
        "affected_crops": "इस रोग से प्रभावित अन्य फसलें:",
        "follow_up": "क्या आप उपचार या बचाव का विवरण चाहते हैं? (हाँ/नहीं)"
    },
    "en": {
        "greet": "Dear farmer,",
        "no_info": "Sorry, no information available for this query.",
        "not_found": "The crop appears to have **{label}**, but we lack specific details in our database.",
        "affected_crops": "Common crops affected:",
        "follow_up": "Do you want treatment or prevention details? (yes/no)"
    },
}

# ----- RAG Global State -----
_FAISS_INDEX = None
_FAISS_METADATA = []
_TFIDF_RETRIEVER = None

try:
    result = rag.initialize_from_dataframe(disease_data, text_column="description")
    if result:
        _FAISS_INDEX, _FAISS_METADATA, _TFIDF_RETRIEVER = result
    logger.info("RAG initialized (Advanced Actions).")
except Exception as e:
    logger.error(f"RAG Init Error: {e}")

# ----- Helper Functions -----

def _translate_response(text: str, target_lang: str) -> str:
    """Fallback-only translator for UI elements. Strictly forbids hallucinations."""
    if target_lang == "en" or not text:
        return text
    
    # FORBID Hallucinations for static labels by using direct lookup
    for lkey, lval in LANG_LABELS["en"].items():
        if text.strip() == lval.strip():
            return LANG_LABELS.get(target_lang, LANG_LABELS["en"]).get(lkey, lval)
            
    lang_map = {"hi": "Hindi", "gu": "Gujarati"}
    lang_name = lang_map.get(target_lang, "Hindi")
    
    prompt = (
        f"Translate the following agricultural response into pure, natural {lang_name}. "
        f"STRICT RULE: Do NOT add any new information. Do NOT try to be helpful. ONLY translate the text provided.\n"
        f"Text to translate:\n{text}"
    )
    translated = generate_text(prompt)
    return translated.strip() if translated else text

def generate_natural_answer(question: str, facts: str, lang: str, history: Optional[str] = None) -> str:
    """Generate a conversational, premium response from facts context."""
    lang_map = {"hi": "Hindi", "gu": "Gujarati", "en": "English"}
    lang_name = lang_map.get(lang, "Hindi")

    prompt = (
        f"You are KisaanAI, a professional and helpful agricultural expert. "
        f"Use the following 'Known Facts' to answer the user's question in natural, conversational {lang_name}.\n\n"
        f"Known Facts:\n{facts}\n\n"
        f"Conversation Context:\n{history if history else 'None'}\n\n"
        f"User Question: {question}\n\n"
        f"STRICT GUIDELINES:\n"
        f"1. Generate a premium, warm, and helpful answer in {lang_name}.\n"
        f"2. CRITICAL: If 'Known Facts' contains specific disease information (Symptoms, Treatment, Prevention), YOU MUST USE THEM. "
        f"DO NOT give generic farming advice if specific data is present.\n"
        f"3. SCRUB AND REMOVE ALL MARATHI OR FOREIGN FRAGMENTS. Only produce pure {lang_name}.\n"
        f"4. Use Markdown (bold, headers, bullet points) for readability.\n"
        f"5. If 'Known Facts' mentions a similar crop, acknowledge it naturally (e.g. 'While I don't have specifics for Peach, here is information on Bacterial Spot based on similar crops like Tomato').\n\n"
        f"Response:"
    )
    return generate_text(prompt)

def _detect_columns(lower: str) -> List[str]:
    """Detect all relevant data columns from user query."""
    cols = []
    if any(k in lower for k in ("symptom", "lakshan", "chinh", "dikha", "dikhta", "kya hota hai", "symptom")):
        cols.append("farmer_symptoms")
    if any(k in lower for k in ("treatment", "cure", "medicine", "upchar", "dava", "daw", "ilaj")):
        cols.append("treatment")
    if any(k in lower for k in ("prevent", "precaution", "bachav", "roktam", "kaise roke", "kaise bachaye")):
        cols.append("prevention")
    if any(k in lower for k in ("duration", "recovery", "samay", "din", "rehta", "time")):
        cols.append("recoverytime")
    if any(k in lower for k in ("crop", "fasil", "konsi crop", "kis me hota hai", "affected crops")):
        cols.append("crop")
    return cols

def _is_correction(text: str) -> bool:
    """Check if the user is correcting the previous bot answer."""
    lower = text.lower()
    # Broaden to catch "it is anthracnose", "not bacterial spot", "i said mango"
    correction_keywords = ["but", "no", "wrong", "galat", "nahi", "nai", "isn't", "is actually", "typing mistake", "not that", "i said", "maine kaha"]
    return any(k in lower for k in correction_keywords)

def _get_conversation_history(tracker: Tracker, max_msgs: int = 20) -> str:
    """Extract last N messages from conversation for LLM context, including image detection."""
    history = []
    
    # Pre-inject image context if available
    metadata = tracker.get_slot("image_metadata") or {}
    detected = metadata.get("detected_disease")
    if detected:
        # Format: Peach___Bacterial_spot -> Peach Bacterial spot
        label = detected.replace("___", " ").replace("_", " ")
        history.append(f"System Context (Observed in last image): {label}")

    # Rasa events are chronological. UserUttered and BotUttered are what we need.
    count = 0
    for event in reversed(tracker.events):
        if count >= max_msgs:
            break
        if event.get("event") == "user":
            history.append(f"User: {event.get('text')}")
            count += 1
        elif event.get("event") == "bot":
            history.append(f"KisaanAI: {event.get('text')}")
            count += 1
    
    history.reverse() # Back to chronological order
    return "\n".join(history)

def _extract_img_label_from_text(text: str) -> Optional[str]:
    """Look for 'Image Analysis: [Label]' in text."""
    if not text: return None
    match = re.search(r"Image Analysis:\s*([^\n]+)", text)
    if match:
        return match.group(1).strip()
    return None

def _smart_detect_language(text: str, current_slot: Optional[str] = None) -> str:
    """Detect language, supporting Romanized text via LLM if needed."""
    lang = detect_language(text)
    if lang == "en":
        # If it's Romanized Hindi/Gujarati, character check returns 'en'.
        # Ask LLM to confirm.
        prompt = (
            f"Detect the language of the following text. Respond with ONE WORD ONLY: 'Hindi', 'Gujarati', or 'English'.\n\n"
            f"Text: {text}"
        )
        detected = generate_text(prompt).strip().lower()
        if "hindi" in detected: return "hi"
        if "gujarati" in detected: return "gu"
    
    return lang or current_slot or "hi"

# ----- Shared Action Logic -----

class ActionHealthConsultant(Action):
    """
    Advanced Action that unifies all disease/crop intelligence.
    Handles both text queries and image recognition metadata.
    """

    def name(self) -> str:
        # Register both for legacy compatibility if needed, 
        # but primarily mapped to action_get_disease_info
        return "action_get_disease_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 1. Logic Setup & Language
        user_msg = tracker.latest_message.get("text", "")
        # RAW LOGGING FOR DIAGNOSIS
        logger.info(f"--- ACTION SERVER DIAGNOSIS ---")
        logger.info(f"Latest Message: '{user_msg}'")
        logger.info(f"Metadata Slot: {tracker.get_slot('image_metadata')}")
        
        metadata = tracker.get_slot("image_metadata") or {}
        if isinstance(metadata, str): 
            metadata = {"detected_disease": metadata}
            
        
        # Smart detection handles Romanized text
        slot_lang = tracker.get_slot("user_language")
        lang = _smart_detect_language(user_msg, current_slot=slot_lang)
        
        labels = LANG_LABELS.get(lang, LANG_LABELS["en"])
        events = [SlotSet("user_language", lang)]
        
        # Get standard history (5 messages is enough for farming context)
        full_history = _get_conversation_history(tracker, max_msgs=5)

        # 2. Disease & Crop Detection
        # BULLETPROOF SCAN: Look for Image Analysis strings anywhere in the recent tracker
        detected_img = None
        for event in reversed(tracker.events):
            # Check both user and bot events (sometimes analysis is echoed back)
            evt_text = (event.get("text") or "") if event.get("event") in ("user", "bot") else ""
            if "Image Analysis:" in evt_text:
                detected_img = _extract_img_label_from_text(evt_text)
                if detected_img:
                    logger.info(f"CAPTURED Image Label from History: {detected_img}")
                    break
        
        # Fallback to slot
        detected_img = detected_img or metadata.get("detected_disease")
        
        slot_disease = tracker.get_slot("disease") or tracker.get_slot("last_disease")
        slot_crop = tracker.get_slot("crop")

        query_en = translate_to_english(user_msg) if lang != "en" else user_msg
        last_answer = tracker.get_slot("last_answer")
        
        # Correction Handling: If user says "but it is X", prioritize text over image metadata
        is_correcting = _is_correction(query_en)
        
        if is_correcting:
            # Re-detect disease specifically from text
            disease, crop = find_disease_smart(query_en, detected_crop=slot_crop)
            if not disease: # Fallback to metadata if text didn't yield a match
                disease = slot_disease
        elif detected_img:
            # Handle format: Crop___Disease from image model
            # Example: Peach___Bacterial_spot
            parts = detected_img.split("___")
            img_crop = parts[0].replace("_", " ") if len(parts) > 1 else None
            # Extract everything after the first '___' as the disease label
            img_label = parts[-1].replace("_", " ") if len(parts) > 0 else detected_img.replace("_", " ")
            
            # Combine for search: "Peach Bacterial spot"
            full_label = f"{img_crop} {img_label}" if img_crop else img_label
            disease, crop = find_disease_smart(full_label, detected_crop=img_crop)
            label = img_label # Fallback display
            logger.info(f"Image-based lookup: '{full_label}' -> Disease: {disease}, Crop: {crop}")
        else:
            disease, crop = find_disease_smart(query_en, detected_crop=slot_crop)
            disease = disease or slot_disease
            crop = crop or slot_crop
            logger.info(f"Text-based lookup: '{query_en}' -> Disease: {disease}, Crop: {crop}")

        if disease:
            events.extend([SlotSet("disease", disease), SlotSet("last_disease", disease)])
        if crop:
            events.append(SlotSet("crop", crop))

        requested_cols = _detect_columns(query_en)
        
        # Specialist Handling: Affirmations (User said "yes" to follow-up)
        if not requested_cols and query_en.strip().lower() in ("yes", "haan", "ha", "sure"):
            if last_answer and ("treatment" in last_answer.lower() or "medicine" in last_answer.lower()):
                requested_cols = ["treatment", "prevention"]

        # 3. Content Retrieval logic
        final_answer = ""
        is_rag = False

        if disease:
            # Path A: Fast CSV Lookup (Precise)
            facts_list = []
            # GREEDY MODE: If we have an image, gather EVERY column from CSV automatically
            search_cols = requested_cols if (requested_cols and not detected_img) else ["farmer_symptoms", "treatment", "prevention", "recoverytime"]
            
            for col in search_cols:
                if col == "crop":
                    all_crops = csv_lookup.get_all_crops_for_disease(disease)
                    if all_crops: facts_list.append(f"Affected Crops: {', '.join(all_crops)}")
                else:
                    val = csv_lookup.get_info_from_csv(disease, col, crop=crop)
                    if val:
                        title = col.replace("farmer_symptoms", "Symptoms").capitalize()
                        facts_list.append(f"### {title}\n{val}")
            
            # Ensure "Affected Crops" is always included even if not requested
            if not requested_cols or "crop" in requested_cols:
                 all_crops = csv_lookup.get_all_crops_for_disease(disease)
                 if all_crops: facts_list.append(f"Affected Crops: {', '.join(all_crops)}")

            if facts_list:
                known_facts = "\n\n".join(facts_list)
                logger.info(f"Retrieved Facts for LLM: {len(known_facts)} chars")
                final_answer = generate_natural_answer(user_msg, known_facts, lang, history=full_history)
            
            # Path B: CSV Full Summary fallback - ONLY if NOTHING specific was requested
            if not final_answer and not requested_cols:
                summary_facts = []
                # If we have a disease, gather ALL standard columns for a full response
                for title, col in [("Symptoms", "farmer_symptoms"), ("Treatment", "treatment"), ("Prevention", "prevention"), ("Recovery Time", "recoverytime")]:
                    v = csv_lookup.get_info_from_csv(disease, col, crop=crop)
                    if v: summary_facts.append(f"### {title}\n{v}")
                
                # Add affected crops info
                all_crops = csv_lookup.get_all_crops_for_disease(disease)
                if all_crops: summary_facts.append(f"### Affected Crops\n{', '.join(all_crops)}")

                if summary_facts:
                    known_facts = "\n\n".join(summary_facts)
                    final_answer = generate_natural_answer(user_msg, known_facts, lang, history=full_history)

        # Path C: RAG (Contextual/Deep) - Use history for better memory
        if not final_answer or len(final_answer) < 30:
            is_rag = True
            retrieved = rag.retrieve(
                f"{query_en} {disease or ''}", top_k=5,
                index=_FAISS_INDEX, metadata=_FAISS_METADATA,
                tfidf_retriever=_TFIDF_RETRIEVER
            )
            # HARDEN RAG: If we have specific columns but no CSV data, focus the LLM
            rag_query = query_en
            if requested_cols and not final_answer:
                aspects = ", ".join(requested_cols)
                rag_query = f"Provide ONLY details about {aspects} for {disease}: {query_en}"
                
            prompt = rag.build_prompt(retrieved, rag_query, history=full_history)
            final_answer = rag.generate_from_prompt(prompt)

        # 4. Final Response Construction
        if not final_answer or "don't know" in final_answer.lower():
            if detected_img:
                display = f"{crop} {label}" if 'label' in locals() else disease
                raw_resp = labels["not_found"].format(label=display)
            else:
                raw_resp = labels["no_info"]
            resp = _translate_response(raw_resp, lang) # Simple fallback items still need translation
        else:
            # If we requested ONLY symptoms, add the follow-up prompt
            if "farmer_symptoms" in requested_cols and len(requested_cols) == 1:
                final_answer += "\n\n" + _translate_response(labels['follow_up'], lang)
            elif not requested_cols and "Symptom" in final_answer:
                 final_answer += "\n\n" + _translate_response(labels['follow_up'], lang)
            
            resp = final_answer # Already generated and localized by generate_natural_answer

        # 5. Dispatch
        dispatcher.utter_message(text=resp)
        
        events.append(SlotSet("last_answer", resp))
        return events

# Keeping separate name for Rasa domain registration if needed, but point to same logic
class ActionGetDiseaseInfoSmart(ActionHealthConsultant):
    def name(self) -> str:
        return "action_get_disease_info_smart"

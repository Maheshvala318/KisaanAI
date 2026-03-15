# Project: KisaanAI (Health Chatbot)

## Overview
A high-performance Rasa-based chatbot for diagnosing agricultural plant diseases. The system integrates advanced image analysis, fuzzy-matched CSV lookups, and RAG (Retrieval-Augmented Generation) to provide accurate treatment and prevention advice in multiple languages (English, Hindi, Gujarati).

## Mission
To empower farmers with instant, accurate, and localized disease diagnosis and treatment recommendations, reducing crop loss and improve agricultural productivity.

## Core Features
1. **Multimodal Analysis**: Combine text queries with image classification labels.
2. **Robust Retrieval**: Hybrid search using formatted CSV data and deep RAG.
3. **Multilingual Support**: Real-time translation and language-specific UI labels.
4. **Hallucination Suppression**: Greedy retrieval and strict fact-citation requirements for LLMs.
5. **Advanced Action Server**: Centralized logic for identification, search, and response generation.

## Current Objective
Stabilizing the retrieval pipeline to ensure that image labels (like "Peach___Bacterial_spot") correctly map to CSV entries and that the bot provides specific, fact-based answers instead of generic hallucinations.

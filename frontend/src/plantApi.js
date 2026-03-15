// plantApi.js
import axios from "axios";

const PLANT_API_URL =
  process.env.REACT_APP_PLANT_API_URL || "http://localhost:8001/predict";

/**
 * Send an image file to plant disease API
 * @param {File} file
 * @returns {Promise<{predicted_index: number, predicted_label: string, probabilities: number[]}>}
 */
export async function classifyPlantImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const resp = await axios.post(PLANT_API_URL, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return resp.data;
}

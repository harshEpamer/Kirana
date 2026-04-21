import axios from "axios";

const BASE_URL = "http://localhost:8004";

export const getSalesByDate = async (date, token) => {
  const params = date ? { date } : {};
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await axios.get(`${BASE_URL}/api/sales/`, { params, headers });
  return res.data;
};

export const getSalesSummary = async (token) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await axios.get(`${BASE_URL}/api/sales/summary`, { headers });
  return res.data;
};

import axios from "axios";

const BASE_URL = "http://localhost:8008";

export const getAllCustomers = async (token) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await axios.get(`${BASE_URL}/api/customers`, { headers });
  return res.data;
};

export const getCustomerHistory = async (userId, token) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await axios.get(`${BASE_URL}/api/customers/${userId}/history`, { headers });
  return res.data;
};

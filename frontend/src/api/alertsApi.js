import { API } from '../config'

export const getLowStockAlerts = () =>
  fetch(`${API.alerts}/alerts/low-stock`).then(r => r.json())

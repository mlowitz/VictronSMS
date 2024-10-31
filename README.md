
### Read Root




| Method | URL |
|--------|-----|
| GET | / |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Get Victron




| Method | URL |
|--------|-----|
| POST | /vrm/ |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Getvalues




| Method | URL |
|--------|-----|
| GET | /vrm/getValues |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Status Message




| Method | URL |
|--------|-----|
| POST | /status/ |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Request Body
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| phoneNumber | string |  | Optional |
| boatName | string |  | Optional |
| installationName | string |  | Optional |
| freshWater1 | string |  | Optional |
| freshWater2 | string |  | Optional |
| lpg1 | string |  | Optional |
| lpg2 | string |  | Optional |
| batterySOC | string |  | Optional |
| poop | string |  | Optional |
| diesel | string |  | Optional |
| tanks | array |  | Optional |

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---

# VIDYUTRAKSHA — Deployment & Infrastructure Guide

## 1. System Requirements

### Hardware Requirements
- **CPU:** 4+ Cores (Intel Xeon / AMD EPYC or Core i5/i7)
- **RAM:** 8 GB Minimum (16 GB Recommended for large raster batches)
- **Disk:** 20 GB SSD storage for local cache & NetCDF / GeoTIFF storage
- **GPU (Optional):** NVIDIA CUDA GPU for batch PyTorch spatiotemporal inference

### Software Requirements
- Python 3.10+
- Node.js 18+ & npm
- Docker & Docker Compose (for containerized deployment)

---

## 2. Production Docker Deployment

```bash
# 1. Clone repository
git clone https://github.com/organization/VIDYUTRAKSHA.git
cd VIDYUTRAKSHA

# 2. Configure environment
cp .env.example .env

# 3. Launch Docker Compose
docker-compose up -d --build

# 4. Verify running services
docker ps
```

- **Frontend Command Centre:** `http://localhost:3000`
- **Backend API Server:** `http://localhost:8000`
- **OpenAPI Interactive Documentation:** `http://localhost:8000/docs`

---

## 3. Manual Local Deployment

### Backend Service:
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m pytest backend/tests -v
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Service:
```bash
cd frontend
npm install
npm run build
npm run dev -- --host 0.0.0.0 --port 5173
```

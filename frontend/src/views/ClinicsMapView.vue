<template>
  <div class="responsive-map-wrapper">
    <div class="responsive-map-container">
      
      <!-- Header -->
      <div class="top-header">
        <button class="icon-btn" @click="$router.go(-1)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h2 class="header-title">Localización de Centros Médicos</h2>
        <div style="width: 24px"></div> <!-- Placeholder for centering -->
      </div>

      <!-- Filters Section -->
      <div class="filters-section">
        <div class="filters-actions">
          <div class="search-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="debouncedFilterChange" 
              placeholder="Buscar centro médico..." 
            />
          </div>
          <div class="select-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
            <select v-model="selectedSpecialty" @change="onFilterChange">
              <option value="">Todas las especialidades</option>
              <option v-for="spec in specialties" :key="spec" :value="spec">{{ spec }}</option>
            </select>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="error-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <p>{{ error }}</p>
      </div>

      <!-- Map Area -->
      <div v-show="!error" class="map-wrapper" :class="{ 'loading-opacity': loading }">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <p>Buscando clínicas...</p>
        </div>
        <div id="clinics-map"></div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import axios from 'axios'

// Fix generic leaflet marker issues with VITE / Vue
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow
});

let mapInstance = null;
const markersLayer = L.layerGroup()
const clinics = ref([])
const specialties = ref([])
const selectedSpecialty = ref("")
const searchQuery = ref("")
const loading = ref(true)
const error = ref(null)

const initMap = () => {
  mapInstance = L.map('clinics-map', {
    zoomControl: false // Move zoom control if needed, or disable default
  }).setView([-16.5, -68.15], 13)

  // Add zoom control to top right to fit the UI design better
  L.control.zoom({
    position: 'topright'
  }).addTo(mapInstance);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance)
  
  markersLayer.addTo(mapInstance)
}

const parseWKT = (wktString) => {
  if (!wktString) return null;
  const regex = /POINT\s*\(\s*([^ ]+)\s+([^ ]+)\s*\)/;
  const match = wktString.match(regex);
  if (match) {
    const lng = parseFloat(match[1]);
    const lat = parseFloat(match[2]);
    return [lat, lng];
  }
  return null;
}

const fetchSpecialties = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const res = await axios.get('http://localhost:8000/api/v1/doctors/specialties/list', {
      headers: { Authorization: `Bearer ${token}` }
    });
    specialties.value = res.data;
  } catch (err) {
    console.error("Error cargando especialidades:", err);
  }
}

const fetchClinics = async () => {
  loading.value = true;
  error.value = null;
  try {
    const token = localStorage.getItem('access_token');
    let url = 'http://localhost:8000/api/v1/clinics/?';
    if (selectedSpecialty.value) {
      url += `specialty=${encodeURIComponent(selectedSpecialty.value)}&`;
    }
    if (searchQuery.value) {
      url += `name=${encodeURIComponent(searchQuery.value)}&`;
    }
    const res = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    clinics.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = 'Ha ocurrido un error cargando las instalaciones médicas.';
  } finally {
    loading.value = false;
  }
}

const onFilterChange = async () => {
  await fetchClinics();
  plotMarkers();
}

let timeoutId = null;
const debouncedFilterChange = () => {
  if (timeoutId) clearTimeout(timeoutId);
  timeoutId = setTimeout(() => {
    onFilterChange();
  }, 500);
}

const plotMarkers = () => {
  if (!mapInstance) return;

  markersLayer.clearLayers();
  let markersAdded = 0;
  const bounds = L.latLngBounds();

  clinics.value.forEach(clinic => {
    if (clinic.location_wkt) {
      const latLng = parseWKT(clinic.location_wkt);
      if (latLng) {
        // Create custom popup content styling
        const popupContent = `
          <div style="font-family: 'Inter', sans-serif; padding: 0.5rem 0;">
            <h4 style="margin: 0 0 0.4rem 0; color: #1e293b; font-size: 1.05rem;">${clinic.name}</h4>
            ${clinic.address ? `<p style="margin: 0 0 0.4rem 0; color: #64748b; font-size: 0.85rem;">${clinic.address}</p>` : ''}
            ${clinic.phone ? `<p style="margin: 0 0 0.8rem 0; color: #0284c7; font-weight: 600; font-size: 0.85rem;">📞 ${clinic.phone}</p>` : ''}
            <button onclick="window.goToDoctorSearch('${clinic.name}')" style="background:#0284c7;color:white;border:none;padding:0.5rem 1rem;border-radius:8px;font-weight:600;width:100%;cursor:pointer;font-family:'Inter', sans-serif;font-size:0.85rem;transition:background 0.2s;">Ver doctores aquí</button>
          </div>
        `;

        const marker = L.marker(latLng).addTo(markersLayer);
        
        marker.bindPopup(popupContent, {
          className: 'custom-popup',
          closeButton: false,
          minWidth: 200
        });
        bounds.extend(latLng);
        markersAdded++;
      }
    }
  });

  if (markersAdded > 0) {
    mapInstance.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
  } else {
    // Zoom out to default if no markers
    mapInstance.setView([-16.5, -68.15], 13);
  }
}

const route = useRoute();
const router = useRouter();

onMounted(async () => {
  window.goToDoctorSearch = (clinicName) => {
    const spec = selectedSpecialty.value || 'Todas';
    router.push({ path: '/patient/appointments/new', query: { search: clinicName, specialty: spec } });
  };

  if (route.query.specialty) {
    selectedSpecialty.value = route.query.specialty;
  }

  await nextTick();
  initMap();
  
  await fetchSpecialties();
  await fetchClinics();
  
  if (!error.value) {
    plotMarkers();
  }
})

onBeforeUnmount(() => {
  if (window.goToDoctorSearch) {
    delete window.goToDoctorSearch;
  }
  if (mapInstance) {
    mapInstance.remove()
  }
})
</script>

<style scoped>
/* Page Wrapper */
.responsive-map-wrapper {
  min-height: 100vh;
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

@media (max-width: 768px) {
  .responsive-map-wrapper { padding: 0; }
}

/* Main Container */
.responsive-map-container {
  width: 100%;
  max-width: 1200px;
  height: 90vh; /* Fixed height to allow map to fill */
  background: #fafafa;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

@media (max-width: 768px) {
  .responsive-map-container {
    height: 100vh;
    border-radius: 0;
  }
}

/* Header */
.top-header { 
  display: flex; align-items: center; justify-content: space-between; 
  padding: 1.25rem 1.5rem; background: white; border-bottom: 1px solid #f1f5f9; 
  flex-shrink: 0; z-index: 10;
}
.icon-btn { 
  background: none; border: none; color: #64748b; cursor: pointer; 
  display: flex; align-items: center; justify-content: center; 
  padding: 0.5rem; border-radius: 50%; transition: background 0.2s, color 0.2s; 
  margin-left: -0.5rem;
}
.icon-btn:hover { background: #f1f5f9; color: #1e293b; }
.header-title { margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b; }

/* Filters Section */
.filters-section {
  background: white;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0; z-index: 10;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}

.filters-actions {
  display: flex;
  gap: 1rem;
  width: 100%;
}

.search-box {
  flex: 1;
}

.select-box {
  min-width: 240px;
}

.search-box, .select-box {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.5rem 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-box:focus-within, .select-box:focus-within {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
  background: white;
}

.search-box svg, .select-box svg { color: #94a3b8; margin-right: 0.5rem; flex-shrink: 0; }

.search-box input, .select-box select {
  border: none;
  background: transparent;
  outline: none;
  font-family: inherit;
  font-size: 0.95rem;
  color: #1e293b;
  width: 100%;
}
.search-box input::placeholder { color: #94a3b8; }
.select-box select { cursor: pointer; appearance: none; padding-right: 1rem; }

@media (max-width: 768px) {
  .filters-actions { flex-direction: column; width: 100%; justify-content: stretch; }
  .search-box, .select-box { width: 100%; }
}

/* Map Area */
.map-wrapper {
  flex: 1;
  position: relative;
  background: #f1f5f9;
}

#clinics-map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Loading & Error States */
.loading-opacity #clinics-map {
  opacity: 0.5;
  filter: blur(1px);
}

.loading-overlay {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 1.5rem 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #0284c7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.loading-overlay p { margin: 0; font-weight: 600; color: #0284c7; }

.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  color: #ef4444;
  background: #fef2f2;
  text-align: center;
  padding: 2rem;
}
.error-state p { margin: 0; font-weight: 600; font-size: 1.1rem; }

/* Custom Leaflet overrides inside map */
:deep(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  padding: 0.25rem;
}
:deep(.leaflet-popup-tip) {
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}
:deep(.leaflet-control-zoom) {
  border: none !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
  border-radius: 8px !important;
  overflow: hidden;
  margin-top: 1.5rem !important;
  margin-right: 1.5rem !important;
}
:deep(.leaflet-control-zoom a) {
  color: #1e293b !important;
  background-color: white !important;
  transition: background 0.2s;
}
:deep(.leaflet-control-zoom a:hover) {
  background-color: #f8fafc !important;
}
</style>

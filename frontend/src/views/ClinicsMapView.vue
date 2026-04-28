<template>
  <div class="standalone-wrapper">
    <div class="map-view-container glass-card">
    <div class="map-header">
      <div class="title-row">
        <button @click="$router.go(-1)" class="back-btn">← Volver</button>
        <h2>Localización de Centros Médicos</h2>
      </div>
      <div class="filter-row">
        <p>Visualiza en tiempo real nuestras clínicas disponibles en la región.</p>
        <div class="filters">
          <input type="text" v-model="searchQuery" @input="debouncedFilterChange" placeholder="Buscar centro médico..." class="form-input search-input" />
          <select v-model="selectedSpecialty" @change="onFilterChange" class="form-input specialty-select">
            <option value="">Todas las especialidades</option>
            <option v-for="spec in specialties" :key="spec" :value="spec">{{ spec }}</option>
          </select>
        </div>
      </div>
    </div>
    
    <div v-if="error" class="error-state">
      {{ error }}
    </div>

    <div v-show="!error" class="map-wrapper" :class="{ 'loading-opacity': loading }">
      <div id="clinics-map"></div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
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
  mapInstance = L.map('clinics-map').setView([-16.5, -68.15], 13)

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
        const marker = L.marker(latLng).addTo(markersLayer);
        
        let popupContent = `<b>${clinic.name}</b>`;
        if (clinic.address) popupContent += `<br/>${clinic.address}`;
        if (clinic.phone) popupContent += `<br/>📞 ${clinic.phone}`;
        
        marker.bindPopup(popupContent);
        bounds.extend(latLng);
        markersAdded++;
      }
    }
  });

  if (markersAdded > 0) {
    mapInstance.fitBounds(bounds, { padding: [50, 50] });
  } else {
    // Zoom out to default if no markers
    mapInstance.setView([-16.5, -68.15], 13);
  }
}

const route = useRoute();

onMounted(async () => {
  if (route.query.specialty) {
    selectedSpecialty.value = route.query.specialty;
  }

  // Asegurar que el div map existe
  await nextTick();
  initMap();
  
  await fetchSpecialties();
  await fetchClinics();
  
  if (!error.value) {
    plotMarkers();
  }
})

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.remove()
  }
})
</script>

<style scoped>
.standalone-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: var(--bg-color);
}
.map-view-container {
  max-width: 1000px; /* Ancho mayor para el mapa */
  width: 90vw;
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.map-header {
  margin-bottom: 1.5rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.back-btn {
  background: white;
  border: 1px solid #E5E7EB;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.2s;
}

.back-btn:hover {
  background: #F3F4F6;
  color: var(--text-main);
}

.title-row h2 {
  color: var(--primary-color);
  margin: 0;
}

.map-wrapper {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
}

#clinics-map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.loading-state, .error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  font-weight: 500;
  color: var(--text-muted);
}

.error-state {
  color: var(--danger-color);
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-row p {
  margin: 0;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #D1D5DB;
  background-color: white;
  min-width: 250px;
  color: var(--text-main);
}

.specialty-select {
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid #D1D5DB;
  background-color: white;
  min-width: 200px;
  color: var(--text-main);
}

.loading-opacity {
  opacity: 0.5;
  transition: opacity 0.3s ease;
}
</style>

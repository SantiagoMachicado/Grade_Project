<template>
  <div class="map-view-container glass-card">
    <div class="map-header">
      <h2>Localización de Centros Médicos</h2>
      <p>Visualiza en tiempo real nuestras clínicas disponibles en la región.</p>
    </div>
    
    <div v-if="loading" class="loading-state">
      Cargando ubicaciones...
    </div>
    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <div v-else class="map-wrapper">
      <div id="clinics-map"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
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

const map = ref(null)
const clinics = ref([])
const loading = ref(true)
const error = ref(null)

const initMap = () => {
  map.value = L.map('clinics-map').setView([-16.5, -68.15], 13)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(map.value)
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

const fetchClinics = async () => {
  loading.value = true;
  error.value = null;
  try {
    const token = localStorage.getItem('access_token');
    const res = await axios.get('http://localhost:8000/api/v1/clinics/', {
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

const plotMarkers = () => {
  if (!map.value) return;

  let markersAdded = 0;
  const bounds = L.latLngBounds();

  clinics.value.forEach(clinic => {
    if (clinic.location_wkt) {
      const latLng = parseWKT(clinic.location_wkt);
      if (latLng) {
        const marker = L.marker(latLng).addTo(map.value);
        
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
    map.value.fitBounds(bounds, { padding: [50, 50] });
  }
}

onMounted(async () => {
  await fetchClinics();
  
  if (!error.value) {
    await nextTick(); // Asegura que el div id="clinics-map" ya existe en el DOM tras quitar "loading"
    initMap();
    plotMarkers();
  }
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
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

.map-header h2 {
  color: var(--primary-color);
  margin-top: 0;
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
</style>

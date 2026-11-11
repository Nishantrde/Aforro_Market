import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';


delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const SimpleMap = () => {
  const position = [12.9145, 77.6365]; // Bengaluru

  return (
    <div style={{ height: '500px', width: '100%' }}>
      <MapContainer center={position} zoom={13} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
        <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        referrerPolicy="strict-origin-when-cross-origin"
        />
        <Marker position={position}>
          <Popup>Sharma Kirana</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};

export default SimpleMap;


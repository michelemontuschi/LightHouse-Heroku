def script():
    return """
            mapboxgl.accessToken = 'pk.eyJ1IjoibWljaGVsZW1vbnR1c2NoaSIsImEiOiJja2dtYzhidDgwanFtMnlvMTU0Zjdra2NsIn0.c9Sa8lhNyhy2_5MBaz52ug';
            var map = new mapboxgl.Map({
                container: '3Dmap',
                zoom: 13.1,
                center: [14.144, 35.413],
                pitch: 85,
                bearing: 80,
                style: 'mapbox://styles/michelemontuschi/cki4pocr80z2519mp1fsw738x'
            });
            map.on('load', function () {
                map.addSource('mapbox-dem', {
                    'type': 'raster-dem',
                    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
                    'tileSize': 512,
                    'maxzoom': 14
                });
            // add the DEM source as a terrain layer with exaggerated height
                map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });
            // add a sky layer that will show when the map is highly pitched
                map.addLayer({
                    'id': 'sky',
                    'type': 'sky',
                    'paint': {
                        'sky-type': 'atmosphere',
                        'sky-atmosphere-sun': [0.0, 0.0],
                        'sky-atmosphere-sun-intensity': 15
                    }
                });
            });
            var marker = new mapboxgl.Marker()
            .setLngLat([14.144, 35.413])
            .addTo(map);
        """
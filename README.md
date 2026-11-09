# Thicken-app

## Ejecutar desde Visual Studio Code

1. Abre la carpeta `Thicken-app` en VS Code (File > Open Folder).
2. Abre una terminal (Terminal > New Terminal) y crea un entorno virtual:
   - Windows:  `python -m venv .venv`  y luego  `.venv\Scripts\activate`
   - macOS/Linux:  `python3 -m venv .venv`  y luego  `source .venv/bin/activate`
3. Instala las dependencias:  `pip install -r requirements.txt`
4. Lanza la app:  `streamlit run ThickenAppFin.py`
5. Se abre en el navegador (http://localhost:8501).

## Estructura

```
Thicken-app/
├── ThickenAppFin.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml          (tema oscuro)
└── assets/
    ├── espesador_hero.jpg   (encabezado)
    ├── espesador_puente.jpg (barra lateral y banda de modelado)
    ├── thickener.png        (sección final)
    └── feedwell aceleration2.png (sección final)
```

Ejecuta siempre `streamlit run` desde la carpeta `Thicken-app` para que se aplique `.streamlit/config.toml`.

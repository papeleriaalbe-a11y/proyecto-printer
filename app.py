from rembg import remove, new_session
import io
from PIL import Image
import os
from flask import Flask, render_template_string, request, send_file
import webbrowser
from threading import Timer
from functools import wraps

app = Flask(__name__)

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
    <title>Centro de Impresiones - Papelería ALBE</title>
    <style>
    
    @import url('https://fonts.googleapis.com/css2?family=Montserrat&family=Roboto&display=swap');
        :root {
            --canvas-width: 21cm;
            --canvas-height: 27.9cm; /* Tamaño carta por defecto */
            --primary-color: #2c3e50;
            --accent-color: #3498db;
            --success-color: #2ecc71;
            --print-color: #e67e22;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 0;
            user-select: none;
            height: 100vh;
            display: flex;
            overflow: hidden; 
        }

        .app-layout {
            display: flex;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }

        .sidebar {
            width: 340px;
            min-width: 340px;
            max-width: 340px;
            background: white;
            box-shadow: 4px 0 15px rgba(0,0,0,0.05);
            padding: 25px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 18px;
            z-index: 10;
            overflow-y: auto;  
            overflow-x: hidden; 
        }

        .main-workspace {
            flex-grow: 1;
            background-color: #f1f5fb; 
            background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
            background-size: 15px 15px;
            overflow: auto; 
            padding: 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            align-items: flex-start; 
        }

        .brand-header {
            text-align: center;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 15px;
        }
        .brand-header h1 {
            color: var(--primary-color);
            margin: 0;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        .brand-header p {
            color: #94a3b8;
            margin: 4px 0 0 0;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .panel-section {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .panel-section label {
            font-weight: 700;
            color: #475569;
            font-size: 13px;
        }
        
        select { 
            padding: 10px; 
            border: 1px solid #cbd5e1; 
            border-radius: 6px; 
            background: #f8fafc; 
            font-weight: 600; 
            font-size: 14px;
            color: var(--primary-color);
            outline: none;
            width: 100%;
            box-sizing: border-box;
        }

        .medidas-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            width: 100%;
            box-sizing: border-box;
        }

        .medida-input-group {
            display: flex;
            flex-direction: column;
            flex: 1;
        }

        .medida-input-group input[type="number"] {
            width: 100%; 
            box-sizing: border-box;
            padding: 10px; 
            border: 1px solid #cbd5e1; 
            border-radius: 6px; 
            background: #f8fafc; 
            font-weight: 600; 
            font-size: 14px;
            color: var(--primary-color);
            outline: none;
            text-align: center;
        }

        .medida-separador {
            font-size: 16px;
            font-weight: bold;
            color: #cbd5e1;
            margin-top: -14px; 
        }

        .medida-label {
            font-size: 10px; 
            color: #64748b; 
            text-align: center; 
            margin-top: 4px;
            font-weight: 600;
        }

        .upload-stack {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .file-zone, .paste-zone {
            border: 2px dashed var(--success-color); 
            background: #f0fdf4; 
            padding: 15px;
            text-align: center; 
            border-radius: 8px; 
            color: #166534; 
            font-weight: 700;
            font-size: 13px;
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center; 
            cursor: pointer;
            box-sizing: border-box;
        }
        .paste-zone { border-color: var(--accent-color); background: #f0f9ff; color: #0369a1; cursor: default; }
        .file-zone input { display: none; }
        
        .btn-add-page {
            width: 100%;
            background-color: #8e44ad;
            color: white;
            border: none;
            padding: 12px;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(142, 68, 173, 0.2);
            transition: background 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-sizing: border-box;
        }
        .btn-add-page:hover { background-color: #732d91; }

        .btn-arrange {
            width: 100%;
            background-color: #34495e;
            color: white;
            border: none;
            padding: 12px;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-sizing: border-box;
        }
        .btn-arrange:hover { background-color: #2c3e50; }

        .btn-print {
            width: 100%; 
            background-color: var(--print-color); 
            color: white; 
            border: none;
            padding: 14px; 
            font-size: 16px; 
            font-weight: 700; 
            border-radius: 8px; 
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(230, 126, 34, 0.2);
            margin-top: auto;
            box-sizing: border-box;
        }
        .btn-print:hover { background-color: #d35400; }

        .workspace-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            margin-bottom: 15px;
            position: sticky;
            left: 0;
        }
        .workspace-title {
            font-weight: 700; 
            color: #64748b; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            font-size: 12px;
            margin: 0;
        }
        
        .zoom-controls {
            display: flex;
            align-items: center;
            gap: 5px;
            background: white;
            padding: 4px 8px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        .btn-zoom {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: none;
            background: #f1f5f9;
            color: #475569;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .zoom-text {
            font-size: 12px;
            font-weight: 700;
            color: #64748b;
            min-width: 45px;
            text-align: center;
        }

        .canvas-container-wrapper {
            padding: 20px;
            display: flex;
            flex-direction: row; 
            gap: 40px; 
            align-items: flex-start;
            transform-origin: top left;
            transition: transform 0.15s ease-out;
        }

        .paper-page {
            width: var(--canvas-width);
            height: var(--canvas-height);
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border: 2px dashed #cbd5e1;
            position: relative;
            box-sizing: border-box;
            overflow: hidden; 
            flex-shrink: 0;
            counter-increment: page-counter;
            transition: border-color 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }

        .paper-page.active-page {
            border: 2px solid var(--accent-color);
            box-shadow: 0 10px 30px rgba(52, 152, 219, 0.2);
        }

        .paper-page::after {
            content: "Hoja " counter(page-counter);
            position: absolute;
            bottom: 15px;
            right: 20px;
            font-size: 11px;
            color: #94a3b8;
            font-weight: bold;
            background: #f1f5fb;
            padding: 4px 8px;
            border-radius: 4px;
            pointer-events: none;
        }

        .paper-page.active-page::after {
            background: #e0f2fe;
            color: var(--accent-color);
        }

        .btn-delete-page-ui {
            position: absolute;
            top: 15px;
            right: 20px;
            background: #ff7675;
            color: white;
            border: none;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            z-index: 50;
            display: none;
        }
        .paper-page:hover .btn-delete-page-ui {
            display: block;
        }
        .btn-delete-page-ui:hover { background: #d63031; }

        .img-container {
            position: absolute;
            border: 1px dashed transparent;
            cursor: move;
            box-sizing: border-box;
            padding: 0;
            overflow: visible;
            transform-origin: center center;
            z-index: 10;
        }
        
        .img-container.selected {
            border-color: var(--accent-color);
            outline: 2px solid #3498db; /* Un borde azul para saber qué está activo */
            outline-offset: 2px;
        }

        .img-crop-wrapper {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
        }

        .img-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: fill;
            display: block;
            pointer-events: none;
        }

        .resizer {
            position: absolute;
            width: 10px;
            height: 10px;
            background: #ffffff;
            border: 2px solid var(--accent-color);
            border-radius: 2px;
            display: none;
            z-index: 30;
        }
        
        .img-container.selected:not(.mode-cropping) .resizer { display: block; }

        .resizer.tl { top: -6px; left: -6px; cursor: nwse-resize; }
        .resizer.tm { top: -6px; left: calc(50% - 6px); cursor: ns-resize; }
.resizer.tr { 
    top: -10px; 
    right: -10px; 
    width: 20px; 
    height: 20px;
    background-color: white; /* Fondo blanco */
    border: 2px solid #3498db; /* Borde azul */
    border-radius: 50%; /* Que sea un círculo */
    cursor: alias; 
    
    /* Centrar el icono */
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #3498db;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    font-weight: bold;
    z-index: 100;
}
        .resizer.ml { top: calc(50% - 6px); left: -6px; cursor: ew-resize; }
        .resizer.mr { top: calc(50% - 6px); right: -6px; cursor: ew-resize; }
        .resizer.bl { bottom: -6px; left: -6px; cursor: nesw-resize; }
        .resizer.bm { bottom: -6px; left: calc(50% - 6px); cursor: ns-resize; }
        .resizer.br { bottom: -6px; right: -6px; cursor: nwse-resize; }

        .crop-line {
            position: absolute;
            background: rgba(230, 126, 34, 0.4);
            display: none; 
            z-index: 40;
        }
        .img-container.selected.mode-cropping .crop-line { display: block; }

        .crop-line.line-t { top: 0; left: 0; width: 100%; height: 6px; cursor: ns-resize; border-bottom: 2px dashed #e67e22; }
        .crop-line.line-b { bottom: 0; left: 0; width: 100%; height: 6px; cursor: ns-resize; border-top: 2px dashed #e67e22; }
        .crop-line.line-l { top: 0; left: 0; height: 100%; width: 6px; cursor: ew-resize; border-right: 2px dashed #e67e22; }
        .crop-line.line-r { top: 0; right: 0; height: 100%; width: 6px; cursor: ew-resize; border-left: 2px dashed #e67e22; }

        #global-tools-menu {
            position: fixed;
            background: rgba(44, 62, 80, 0.98);
            padding: 6px 10px;
            border-radius: 6px;
            display: none; 
            gap: 8px;
            z-index: 99999; 
            white-space: nowrap;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            pointer-events: auto;
        }
        
        #global-tools-menu label, #global-tools-menu button {
            color: white; font-size: 11px; font-weight: bold; background: none; border: none; cursor: pointer;
        }
        #global-tools-menu input[type="number"] {
            width: 45px; padding: 2px; font-size: 11px; text-align: center; border-radius: 3px; border: none; color: black;
        }
        .btn-action-del { color: #ff7675 !important; }
        .btn-action-crop { color: #ffeaa7 !important; }
        .btn-action-crop.active { color: #2ecc71 !important; }

        /* 🛠️ SOLUCIÓN DEFINITIVA PARA IMPRESIÓN MULTIPÁGINA */
        @media print {
            @page {
                margin: 0;
            }
            
            /* Eliminamos flex y comportamientos fijos de pantalla completa */
            html, body { 
                background: white !important; 
                padding: 0 !important; 
                margin: 0 !important; 
                display: block !important; 
                overflow: visible !important; 
                height: auto !important;
                width: auto !important;
            }
            
            .app-layout {
                display: block !important;
                overflow: visible !important;
                width: auto !important;
                height: auto !important;
            }

            .sidebar, .workspace-header, #global-tools-menu, .resizer, .crop-line, .btn-delete-page-ui { 
                display: none !important; 
            }
            
            .main-workspace { 
                padding: 0 !important; 
                background: white !important; 
                display: block !important; 
                overflow: visible !important; 
                width: auto !important;
                height: auto !important;
            }
            
            /* CRÍTICO: 'transform: none' elimina el bug de escala que clonaba la hoja 1 */
            .canvas-container-wrapper { 
                padding: 0 !important; 
                display: block !important; 
                transform: none !important; 
                gap: 0 !important; 
                overflow: visible !important;
                width: auto !important;
                height: auto !important;
            }
            
            .paper-page { 
                width: var(--canvas-width) !important; 
                height: var(--canvas-height) !important; 
                margin: 0 !important; 
                padding: 0 !important; 
                box-shadow: none !important; 
                border: none !important; 
                display: block !important;
                page-break-after: always !important; 
                break-after: page !important;
                overflow: hidden !important;
                position: relative !important;
            }
            
            .paper-page::after { display: none !important; } 
            .img-container { border: none !important; }
        }
        
/* Estilo del nodo que inyectaremos */
.rotate-handle {
    width: 14px;
    height: 14px;
    background-color: #3498db;
    border: 2px solid white;
    border-radius: 50%;
    position: absolute;
    top: -30px; /* Separado arriba de la imagen */
    left: 50%;
    transform: translateX(-50%);
    cursor: grab;
    z-index: 100;
}

.btn-paste-float {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background-color: #2ecc71; /* Verde positivo para "Acción" */
    color: white;
    border-radius: 50%;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    z-index: 1000;
    transition: transform 0.2s, background-color 0.2s;
}

.btn-paste-float:hover {
    transform: scale(1.1);
    background-color: #27ae60;
}





.text-container {
    position: absolute !important;
    /* Cambiamos 'transparent' por un color muy suave para que siempre sea visible */
    border: 2px dashed #cccccc; 
    cursor: move;
    box-sizing: border-box;
    z-index: 10;
    /* Agregamos una transición para que se vea profesional */
    transition: border 0.2s ease;
}

/* EFECTO HOVER: Ayuda al usuario a localizar el cuadro antes de hacer clic */
.text-container:hover {
    border: 2px dashed #3498db;
    background-color: rgba(52, 152, 219, 0.05); /* Un fondo muy sutil al pasar el mouse */
}

.text-container.selected {
    border: 1px solid #3498db !important;
    background-color: transparent;
}

/* El nodo resizer solo aparece dentro de un text-container seleccionado */
.text-container.selected .resizer {
    display: block !important;
}

/* Ajuste específico para que el contenido sea editable */
.text-container [contenteditable="true"] {
    width: 100%;
    height: 100%;
    outline: none;
    padding: 10px;
    cursor: text;
    /* Evita que el usuario tenga que hacer clic exactamente en el borde */
    min-width: 30px;
    min-height: 30px;
}

    </style>
</head>
<body>

<div class="app-layout">
    <aside class="sidebar">
        <div class="brand-header">
            <h1>Papelería ALBE</h1>
            <p>Centro de Impresiones</p>
        </div>

        <div class="panel-section">
            <label for="tipo-papel">1. Tipo de Papel:</label>
            <select id="tipo-papel" onchange="actualizarDimensionesPapel()">
                <option value="carta" selected>Tamaño Carta</option>
                <option value="oficio">Tamaño Oficio</option>
                <option value="a4">Tamaño A4</option>
            </select>
        </div>

        <div class="panel-section">
            <label>2. Medidas de Entrada (cm):</label>
            <div class="medidas-container">
                <div class="medida-input-group">
                    <input type="number" id="global-ancho" value="6" step="0.5" oninput="actualizarTamanoGlobal()">
                    <span class="medida-label">Ancho</span>
                </div>
                <span class="medida-separador">×</span>
                <div class="medida-input-group">
                    <input type="number" id="global-alto" value="6" step="0.5" oninput="actualizarTamanoGlobal()">
                    <span class="medida-label">Alto</span>
                </div>
            </div>
        </div>

        <div class="panel-section" style="margin-top: 5px;">
            <label>3. Control de Páginas:</label>
            <button class="btn-add-page" onclick="agregarNuevaHojaManual()">➕ Agregar Nueva Hoja</button>
            <button class="btn-limpiar" onclick="limpiarHojaActual()" style="margin-top: 10px; background-color: #e74c3c; color: white; border: none; padding: 10px; border-radius: 8px; cursor: pointer;">
            🧹 Limpiar Hoja Actual
        </button>
        </div>

        <div class="panel-section" style="margin-top: 5px;">
            <label>4. Cargar Fotos:</label>
            <div class="upload-stack">
                <label class="file-zone" for="input-archivos">
                    <span>📁 Buscar Archivos</span>
                    <input type="file" id="input-archivos" multiple accept="image/*" onchange="cargarDesdeArchivos(this)">
                </label>
                
                <div class="paste-zone" id="zona-pegado">
                    <span>📋 Pegar de WhatsApp</span>
                    <span style="font-size: 10px; font-weight: normal; opacity: 0.8; margin-top: 2px;">(Ctrl + V en cualquier lado)</span>
                </div>
            </div>
        </div>

        <div class="panel-section" style="margin-top: 5px;">
            <label>5. Organizar Selección:</label>
            <button class="btn-arrange" onclick="acomodarImagenesEnHojaActiva()">✨ Acomodar en esta Hoja</button>
            <button type="button" onclick="crearCuadroTexto()" style="padding: 8px 12px; cursor: pointer;">
    ➕ Agregar Texto
</button>
        </div>

        <button class="btn-print" onclick="window.print()">⚡ ENVIAR A IMPRESORA</button>
    </aside>

    <main class="main-workspace" id="workspace-scroll-area">
        <div class="workspace-header">
            <h2 class="workspace-title">Vista Previa de Impresión</h2>
            <div class="zoom-controls">
                <button type="button" class="btn-zoom" onclick="cambiarZoom(-0.1)">-</button>
                <span class="zoom-text" id="zoom-lbl">100%</span>
                <button type="button" class="btn-zoom" onclick="cambiarZoom(0.1)">+</button>
            </div>
        </div>
        
        <div class="canvas-container-wrapper" id="canvas-wrapper">
            <div class="paper-page active-page" id="page-1"></div>
        </div>
    </main>
</div>

<div id="global-tools-menu">
    <div class="tools-img" style="display: flex; gap: 5px; align-items: center;">
        <input type="number" class="ancho-num" step="0.1" style="width: 60px;"> cm
        <input type="number" class="alto-num" step="0.1" style="width: 60px;"> cm
        <button type="button" class="btn-action-crop" id="g-btn-crop">✂️ Recortar</button>
        <button type="button" class="btn-action-bg" onclick="ejecutarQuitarFondo()" style="color: #2ecc71; background: none; border: none; cursor: pointer;">✨ Fondo</button>
        <button type="button" class="btn-rotar" id="g-btn-rotate">🔄 Girar</button>
    </div>

    <div class="tools-text" style="display: none; gap: 5px; align-items: center;">
        <select onchange="formatoTexto('fontName', this.value)">
    <option value="Arial">Arial</option>
    <option value="Verdana">Verdana</option>
    <option value="Helvetica">Helvetica</option>
    <option value="Segoe UI">Segoe UI</option>
    
    <option value="Times New Roman">Times New Roman</option>
    <option value="Georgia">Georgia</option>
    <option value="Palatino">Palatino</option>
    
    <option value="Courier New">Courier</option>
    <option value="Consolas">Consolas</option>
    <option value="Montserrat">Montserrat</option>
    <option value="Roboto">Roboto</option>
</select>
        <button onmousedown="event.preventDefault(); formatoTexto('bold')"><b>B</b></button>
        <button onmousedown="event.preventDefault(); formatoTexto('italic')"><i>I</i></button>
        <button onmousedown="event.preventDefault(); formatoTexto('underline')"><u>U</u></button>
        <button onmousedown="event.preventDefault(); formatoTexto('justifyLeft')">⬅️</button>
        <button onmousedown="event.preventDefault(); formatoTexto('justifyCenter')">↔️</button>
        <button onmousedown="event.preventDefault(); formatoTexto('justifyRight')">➡️</button>
        <button onclick="cambiarTamanio(2)">A+</button>
        <button onclick="cambiarTamanio(-2)">A-</button>
        <input type="color" onchange="formatoTexto('foreColor', this.value)">
    </div>

    <div class="tools-common" style="display: flex; gap: 5px; border-left: 1px solid #ccc; padding-left: 5px;">
        <button type="button" onclick="deshacerCambios()" style="color: #f1c40f; background: none; border: none; cursor: pointer;">↩️</button>
        <button type="button" onclick="traerAlFrente()" title="Frente" style="background: none; border: none; cursor: pointer;">🔼</button>
        <button type="button" onclick="enviarAlFondo()" title="Fondo" style="background: none; border: none; cursor: pointer;">🔽</button>
        <button type="button" class="btn-action-del" id="g-btn-delete" style="color: red; background: none; border: none; cursor: pointer;">❌</button>
    </div>
</div>

<script>
    const CM_A_PX = 37.8; 
    const DIMENSIONES = {
        carta: { w: '21cm', h: '27.9cm' },
        oficio: { w: '21.6cm', h: '35.6cm' },
        a4: { w: '21cm', h: '29.7cm' }
    };

    let imagenIdContador = 0;
    let hojaIdContador = 1;
    let elementoSeleccionado = null;
    let nivelZoomActual = 1.0; 

    function actualizarDimensionesPapel() {
        const tipo = document.getElementById('tipo-papel').value;
        document.documentElement.style.setProperty('--canvas-width', DIMENSIONES[tipo].w);
        document.documentElement.style.setProperty('--canvas-height', DIMENSIONES[tipo].h);
        reposicionarMenuGlobal();
    }

    function cambiarZoom(factor) {
        nivelZoomActual += factor;
        if (nivelZoomActual < 0.5) nivelZoomActual = 0.5;
        if (nivelZoomActual > 2.0) nivelZoomActual = 2.0;
        document.getElementById('canvas-wrapper').style.transform = `scale(${nivelZoomActual})`;
        document.getElementById('zoom-lbl').innerText = Math.round(nivelZoomActual * 100) + '%';
        reposicionarMenuGlobal();
    }

function reposicionarMenuGlobal() {
        const menu = document.getElementById('global-tools-menu');
        if (!elementoSeleccionado) {
            menu.style.display = 'none';
            return;
        }
        
        // --- NUEVA LÓGICA CONTEXTUAL ---
    // Detectamos si lo seleccionado tiene un campo de texto editable
    const esTexto = elementoSeleccionado.querySelector('[contenteditable="true"]');
    
    // Mostramos/Ocultamos los grupos basándonos en si es texto o imagen
    const grupoImagen = menu.querySelector('.tools-img');
    const grupoTexto = menu.querySelector('.tools-text');
    
    if (grupoImagen) grupoImagen.style.display = esTexto ? 'none' : 'flex';
    if (grupoTexto) grupoTexto.style.display = esTexto ? 'flex' : 'none';
    // --------------------------------
        menu.style.display = 'flex';
        const box = elementoSeleccionado.getBoundingClientRect();
        const menuWidth = menu.offsetWidth || 315;
        
        let targetLeft = box.left + (box.width / 2) - (menuWidth / 2);
        
        // --- AQUÍ ESTÁ LA SOLUCIÓN ---
        // Si hay un nodo de rotación, el menú debe ir abajo (targetTop = box.bottom + 10)
        // De lo contrario, lo dejamos arriba como estaba (box.top - 42)
        const tieneNodo = elementoSeleccionado.querySelector('.rotate-handle');
        let targetTop = tieneNodo ? (box.bottom + 10) : (box.top - 42);

        // Ajustes para que no se salga de la pantalla
        if (targetLeft < 350) targetLeft = 350; 
        if (targetLeft + menuWidth > window.innerWidth) targetLeft = window.innerWidth - menuWidth - 15;
        
        // Si al intentar ponerlo abajo queda fuera de la pantalla, lo forzamos arriba
        if (targetTop + 60 > window.innerHeight) targetTop = box.top - 42;

        menu.style.left = targetLeft + 'px';
        menu.style.top = targetTop + 'px';
    }

    document.getElementById('workspace-scroll-area').addEventListener('scroll', reposicionarMenuGlobal);

    function seleccionarHojaDestino(hojaElemento) {
        document.querySelectorAll('.paper-page').forEach(h => h.classList.remove('active-page'));
        hojaElemento.classList.add('active-page');
    }

    function obtenerHojaActiva() {
        let activa = document.querySelector('.paper-page.active-page');
        if (!activa) {
            activa = document.querySelector('.paper-page');
            if (activa) activa.classList.add('active-page');
        }
        return activa;
    }

function agregarNuevaHojaManual() {
    hojaIdContador++;
    const wrapper = document.getElementById('canvas-wrapper');
    
    const nuevaHoja = document.createElement('div');
    nuevaHoja.className = 'paper-page';
    nuevaHoja.id = 'page-' + hojaIdContador;
    
    nuevaHoja.addEventListener('mousedown', function(e) {
        seleccionarHojaDestino(nuevaHoja);
        if (e.target === this) deseleccionarTodo();
    });

    const btnDel = document.createElement('button');
    btnDel.className = 'btn-delete-page-ui';
    btnDel.innerText = '🗑️ Quitar';
    
    btnDel.onclick = function(e) {
        e.stopPropagation();
        
        // Integración de SweetAlert2
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Se borrarán también las imágenes que tiene adentro.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, quitar hoja',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Eliminar la hoja del DOM
                nuevaHoja.remove();
                
                // Actualizar la referencia de la hoja activa (asegura que el sistema no se rompa)
                const hojasRestantes = document.querySelectorAll('.paper-page');
                if (hojasRestantes.length > 0) {
                    seleccionarHojaDestino(hojasRestantes[hojasRestantes.length - 1]);
                }
                
                deseleccionarTodo();
                
                Swal.fire('Eliminado', 'La hoja ha sido quitada.', 'success');
            }
        });
    };
    
    nuevaHoja.appendChild(btnDel);
    wrapper.appendChild(nuevaHoja);
    seleccionarHojaDestino(nuevaHoja); 
}

    function actualizarTamanoGlobal() {
        const wCm = parseFloat(document.getElementById('global-ancho').value);
        const hCm = parseFloat(document.getElementById('global-alto').value);
        if (isNaN(wCm) || isNaN(hCm)) return;

        document.querySelectorAll('.img-container').forEach(container => {
            if (container.classList.contains('mode-cropping')) return;
            
            container.style.width = (wCm * CM_A_PX) + 'px';
            container.style.height = (hCm * CM_A_PX) + 'px';
            
            const img = container.querySelector('img');
            img.style.width = '100%'; img.style.height = '100%';
            img.style.left = '0px'; img.style.top = '0px';
            container.dataset.cropLeftPx = 0; container.dataset.cropTopPx = 0;
            
            if (container === elementoSeleccionado) actualizarInputsNumericos(container);
        });
        
        acomodarImagenesEnHojaActiva();
    }

    function acomodarImagenesEnHojaActiva() {
        const hoja = obtenerHojaActiva();
        if (!hoja) return;

        const contenedores = Array.from(hoja.querySelectorAll('.img-container'));
        if (contenedores.length === 0) return;

        const margenPx = 25; 
        const espacioPx = 15; 
        const anchoHojaPx = hoja.clientWidth;
        const altoHojaPx = hoja.clientHeight;
        const anchoMaximoFotos = anchoHojaPx - (margenPx * 2);

        let xActual = margenPx;
        let yActual = margenPx;
        let altoMaximoDeFilaActual = 0;

        contenedores.forEach(container => {
            let wFoto = container.offsetWidth;
            let hFoto = container.offsetHeight;

            if (wFoto > anchoMaximoFotos) wFoto = anchoMaximoFotos;

            if (xActual + wFoto > anchoHojaPx - margenPx) {
                xActual = margenPx;
                yActual += altoMaximoDeFilaActual + espacioPx;
                altoMaximoDeFilaActual = 0;
            }

            container.style.left = xActual + 'px';
            container.style.top = yActual + 'px';

            xActual += wFoto + espacioPx;
            if (hFoto > altoMaximoDeFilaActual) altoMaximoDeFilaActual = hFoto;

            if (container === elementoSeleccionado) actualizarInputsNumericos(container);
        });

        reposicionarMenuGlobal();
    }

    function deseleccionarTodo() {
        document.querySelectorAll('.img-container').forEach(el => {
            el.classList.remove('selected', 'mode-cropping');
        });
        elementoSeleccionado = null;
        reposicionarMenuGlobal();
    }

    document.addEventListener('paste', function (e) {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") === 0) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                reader.onload = function (event) { agregarImagen(event.target.result); };
                reader.readAsDataURL(blob);
            }
        }
    });

    function cargarDesdeArchivos(input) {
        if (input.files && input.files.length > 0) {
            for (let i = 0; i < input.files.length; i++) {
                const reader = new FileReader();
                reader.onload = function (e) { agregarImagen(e.target.result); }
                reader.readAsDataURL(input.files[i]);
            }
            input.value = ""; 
        }
    }

    function agregarImagen(base64Data) {
        imagenIdContador++;
        
        const container = document.createElement('div');
        container.className = 'img-container';
        container.id = 'img-box-' + imagenIdContador;
        
        container.dataset.cropLeftPx = 0;
        container.dataset.cropTopPx = 0;
        container.dataset.history = JSON.stringify([]);
        container.dataset.rotation = "0"; 
        
        const wCm = parseFloat(document.getElementById('global-ancho').value);
        const hCm = parseFloat(document.getElementById('global-alto').value);
        
        const widthPx = wCm * CM_A_PX;
        const heightPx = hCm * CM_A_PX;
        
        container.style.width = widthPx + 'px';
        container.style.height = heightPx + 'px';
        
        const wrapper = document.createElement('div');
        wrapper.className = 'img-crop-wrapper';
        
        const img = document.createElement('img');
        img.src = base64Data;
        img.style.width = widthPx + 'px';
        img.style.height = heightPx + 'px';
        img.style.left = '0px'; img.style.top = '0px';
        
        wrapper.appendChild(img);
        container.appendChild(wrapper);

        const posiciones = ['tl', 'tm', 'tr', 'ml', 'mr', 'bl', 'bm', 'br'];
        posiciones.forEach(pos => {
            const resizer = document.createElement('div');
            resizer.className = `resizer ${pos}`;
            if (pos === 'tr') {
        resizer.innerHTML = '↻'; 
        resizer.style.display = 'flex';
        resizer.style.alignItems = 'center';
        resizer.style.justifyContent = 'center';
        resizer.style.fontSize = '14px';
        resizer.style.color = '#3498db';
    }
            container.appendChild(resizer);
        });

        const lineas = ['t', 'b', 'l', 'r'];
        lineas.forEach(l => {
            const lineEl = document.createElement('div');
            lineEl.className = `crop-line line-${l}`;
            container.appendChild(lineEl);
        });

        const destino = obtenerHojaActiva();
        destino.appendChild(container);

        hacerInteractiva(container);
        
        deseleccionarTodo();
        container.classList.add('selected');
        elementoSeleccionado = container;
        
        actualizarInputsNumericos(container);
        acomodarImagenesEnHojaActiva();
    }

    function actualizarInputsNumericos(container) {
        const menu = document.getElementById('global-tools-menu');
        menu.querySelector('.ancho-num').value = (container.offsetWidth / CM_A_PX).toFixed(1);
        menu.querySelector('.alto-num').value = (container.offsetHeight / CM_A_PX).toFixed(1);
        
        const btnCrop = document.getElementById('g-btn-crop');
        if (container.classList.contains('mode-cropping')) {
            btnCrop.classList.add('active');
            btnCrop.innerText = '👁️ Mover';
        } else {
            btnCrop.classList.remove('active');
            btnCrop.innerText = '✂️ Recortar';
        }
    }

    function guardarEstadoHistorial(container) {
        let historial = JSON.parse(container.dataset.history || "[]");
        const img = container.querySelector('img');
        let estado = {
            cWidth: container.style.width, cHeight: container.style.height,
            cLeft: container.style.left, cTop: container.style.top,
            imgWidth: img.style.width, imgHeight: img.style.height,
            imgLeft: img.style.left, imgTop: img.style.top,
            cropLeftPx: container.dataset.cropLeftPx, cropTopPx: container.dataset.cropTopPx
        };
        historial.push(estado);
        container.dataset.history = JSON.stringify(historial);
    }

    function deshacerUltimoRecorte(container) {
        let historial = JSON.parse(container.dataset.history || "[]");
        if (historial.length === 0) return;
        
        let ultimoEstado = historial.pop();
        container.dataset.history = JSON.stringify(historial);
        const img = container.querySelector('img');
        
        container.style.width = ultimoEstado.cWidth; container.style.height = ultimoEstado.cHeight;
        container.style.left = ultimoEstado.cLeft; container.style.top = ultimoEstado.cTop;
        img.style.width = ultimoEstado.imgWidth; img.style.height = ultimoEstado.imgHeight;
        img.style.left = ultimoEstado.imgLeft; img.style.top = ultimoEstado.imgTop;
        container.dataset.cropLeftPx = ultimoEstado.cropLeftPx; container.dataset.cropTopPx = ultimoEstado.cropTopPx;
        
        if (container === elementoSeleccionado) actualizarInputsNumericos(container);
    }
    
    
    
function hacerTextoInteractiva(container) {
    const resizer = container.querySelector('.resizer');
    const editable = container.querySelector('.texto-editable'); // Asegúrate que tu HTML tenga esta clase
    const padre = container.parentElement;

    // 1. Mover y Seleccionar
    container.addEventListener('mousedown', function(e) {
        // A) Siempre seleccionamos el elemento al hacer clic (y mostramos el menú)
        if (!container.classList.contains('selected')) {
            document.querySelectorAll('.img-container').forEach(el => el.classList.remove('selected'));
            container.classList.add('selected');
            elementoSeleccionado = container;
            reposicionarMenuGlobal();
        }

        // B) Si tocamos el resizer, NO movemos, dejamos que el otro evento actúe
        if (e.target === resizer) return;

        // C) Si tocamos el texto editable, NO movemos el cuadro, dejamos que el usuario escriba
        if (e.target === editable) return;

        // D) Si llegamos aquí, es porque tocamos el "borde" o "fondo" del contenedor: INICIAMOS ARRASTRE
        const padreRect = padre.getBoundingClientRect();
        let shiftX = (e.clientX - container.getBoundingClientRect().left);
        let shiftY = (e.clientY - container.getBoundingClientRect().top);

        function moveAt(pageX, pageY) {
            // Ajuste por zoom: si tu sistema tiene zoom, divide el resultado por el factor de zoom
            let newLeft = (pageX - padreRect.left - shiftX);
            let newTop = (pageY - padreRect.top - shiftY);
            
            container.style.left = newLeft + 'px';
            container.style.top = newTop + 'px';
        }

        function onMouseMove(e) {
            moveAt(e.pageX, e.pageY);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', function() {
            document.removeEventListener('mousemove', onMouseMove);
        }, { once: true });
    });

    // 2. Redimensionar
    resizer.addEventListener('mousedown', function(e) {
        e.stopPropagation();
        e.preventDefault();
        
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = container.offsetWidth;
        const startHeight = container.offsetHeight;

        function onMouseMove(moveEvent) {
            container.style.width = Math.max(50, startWidth + (moveEvent.clientX - startX)) + 'px';
            container.style.height = Math.max(30, startHeight + (moveEvent.clientY - startY)) + 'px';
        }

        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            reposicionarMenuGlobal();
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });
}
    
    
    
    
    
    

    function hacerInteractiva(container) {
        const img = container.querySelector('img');

        container.addEventListener('mousedown', function(e) {
            if (e.target.classList.contains('resizer') || e.target.classList.contains('crop-line')) return; 
            
            // Si presionas Ctrl, sumas a la selección. Si no, reseteas todo.
    if (!e.ctrlKey) {
        document.querySelectorAll('.img-container').forEach(c => c.classList.remove('selected'));
    }
    
    container.classList.add('selected');
    elementoSeleccionado = container;
            
            const hojaPadre = container.parentElement;
            seleccionarHojaDestino(hojaPadre);

            if (!container.classList.contains('selected')) {
                deseleccionarTodo();
                container.classList.add('selected');
                elementoSeleccionado = container;
                agregarNodoRotacion(container);
                actualizarInputsNumericos(container);
            }
            
            reposicionarMenuGlobal();
            
            let shiftX = (e.clientX - container.getBoundingClientRect().left) / nivelZoomActual;
            let shiftY = (e.clientY - container.getBoundingClientRect().top) / nivelZoomActual;
            const padreRect = hojaPadre.getBoundingClientRect();

            function moverA(clientX, clientY) {
    // 1. Calculamos la posición base
    let nuevaLeft = ((clientX - padreRect.left) / nivelZoomActual - shiftX);
    let nuevaTop = ((clientY - padreRect.top) / nivelZoomActual - shiftY);

    // --- NUEVO: Lógica de Snapping ---
    const umbral = 15; // Qué tan fuerte es el imán en píxeles
    
    // Snapping contra los bordes de la hoja (padreRect)
    if (Math.abs(nuevaLeft) < umbral) nuevaLeft = 0;
    if (Math.abs(nuevaTop) < umbral) nuevaTop = 0;

    // Snapping contra otros elementos (solo si NO están seleccionados)
    document.querySelectorAll('.img-container:not(.selected)').forEach(otra => {
        const rect = otra.getBoundingClientRect();
        // Convertimos la posición de la "otra" al sistema de coordenadas de tu hoja
        const otraLeft = (rect.left - padreRect.left) / nivelZoomActual;
        const otraTop = (rect.top - padreRect.top) / nivelZoomActual;

        if (Math.abs(nuevaLeft - otraLeft) < umbral) nuevaLeft = otraLeft;
        if (Math.abs(nuevaTop - otraTop) < umbral) nuevaTop = otraTop;
    });
    // ---------------------------------

    // 2. Calculamos los deltas basados en la posición corregida
    const deltaX = nuevaLeft - parseFloat(container.style.left);
    const deltaY = nuevaTop - parseFloat(container.style.top);

    // 3. Movemos el contenedor principal
    container.style.left = nuevaLeft + 'px';
    container.style.top = nuevaTop + 'px';

    // 4. Movemos los seleccionados
    const seleccionados = document.querySelectorAll('.img-container.selected');
    seleccionados.forEach(img => {
        if (img !== container) {
            img.style.left = (parseFloat(img.style.left || 0) + deltaX) + 'px';
            img.style.top = (parseFloat(img.style.top || 0) + deltaY) + 'px';
        }
    });

    reposicionarMenuGlobal(); 
}
            function onMouseMove(e) { moverA(e.clientX, e.clientY); }
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', function() {
                document.removeEventListener('mousemove', onMouseMove);
            }, { once: true });
        });

        const resizers = container.querySelectorAll('.resizer');
        resizers.forEach(resizer => {
            resizer.addEventListener('mousedown', function(e) {
                e.stopPropagation();
                const tipo = e.target.classList[1];
                if (tipo === 'tr') {
                    iniciarRotacion(container, e);
                    return; // Salimos para que no ejecute el resize de abajo
                }
                
                // --- AQUÍ GUARDAMOS EL ESTADO ORIGINAL DE TODO EL GRUPO ---
    // Esto es lo que evita que el redimensionamiento sea "sensible" o errático
    document.querySelectorAll('.img-container.selected').forEach(el => {
        el.dataset.origW = parseFloat(el.style.width);
        el.dataset.origH = parseFloat(el.style.height);
        const img = el.querySelector('img');
        img.dataset.origImgW = parseFloat(img.style.width);
        img.dataset.origImgH = parseFloat(img.style.height);
    });
                const startWidth = container.offsetWidth; const startHeight = container.offsetHeight;
                const startLeft = container.offsetLeft; const startTop = container.offsetTop;
                const startImgW = parseFloat(img.style.width); const startImgH = parseFloat(img.style.height);
                const startImgL = parseFloat(img.style.left); const startImgT = parseFloat(img.style.top);
                const startCropLeft = parseFloat(container.dataset.cropLeftPx || 0);
                const startCropTop = parseFloat(container.dataset.cropTopPx || 0);
                const startX = e.clientX; const startY = e.clientY;

                function onMouseMoveResize(event) {
    let diffX = (event.clientX - startX) / nivelZoomActual;
    let diffY = (event.clientY - startY) / nivelZoomActual;
    let ratioX = 1; let ratioY = 1;

    // 1. Calculamos el ratio basado en el contenedor principal
    if (tipo.includes('r')) {
        let nw = startWidth + diffX;
        if (nw > 15) ratioX = nw / startWidth;
    }
    if (tipo.includes('b')) {
        let nh = startHeight + diffY;
        if (nh > 15) ratioY = nh / startHeight;
    }
    if (tipo.includes('l')) {
        let nw = startWidth - diffX;
        if (nw > 15) ratioX = nw / startWidth;
    }
    if (tipo.includes('t')) {
        let nh = startHeight - diffY;
        if (nh > 15) ratioY = nh / startHeight;
    }

    // 2. Aplicamos cambios a TODOS los seleccionados
    const seleccionados = document.querySelectorAll('.img-container.selected');
    
    seleccionados.forEach(c => {
        // Obtenemos los valores "originales" guardados al iniciar el drag
        // Si no existen, usamos el valor actual como fallback
        const origW = parseFloat(c.dataset.origW || c.style.width);
        const origH = parseFloat(c.dataset.origH || c.style.height);
        
        const cImg = c.querySelector('img');
        const origImgW = parseFloat(cImg.dataset.origImgW || cImg.style.width);
        const origImgH = parseFloat(cImg.dataset.origImgH || cImg.style.height);

        // Aplicamos el ratio sobre el valor ORIGINAL (no sobre el actual)
        if (ratioX !== 1) {
            c.style.width = (origW * ratioX) + 'px';
            cImg.style.width = (origImgW * ratioX) + 'px';
        }
        if (ratioY !== 1) {
            c.style.height = (origH * ratioY) + 'px';
            cImg.style.height = (origImgH * ratioY) + 'px';
        }
    });

    if (container === elementoSeleccionado) actualizarInputsNumericos(container);
    reposicionarMenuGlobal();
}
                document.addEventListener('mousemove', onMouseMoveResize);
                document.addEventListener('mouseup', function() {
                    document.removeEventListener('mousemove', onMouseMoveResize);
                }, { once: true });
            });
        });

        const cropLines = container.querySelectorAll('.crop-line');
        cropLines.forEach(line => {
            line.addEventListener('mousedown', function(e) {
                e.stopPropagation();
                guardarEstadoHistorial(container);

                const lado = e.target.classList[1].split('-')[1];
                const startX = e.clientX; const startY = e.clientY;
                const startWidth = container.offsetWidth; const startHeight = container.offsetHeight;
                const startLeft = container.offsetLeft; const startTop = container.offsetTop;
                const startImgW = parseFloat(img.style.width); const startImgH = parseFloat(img.style.height);
                const startImgL = parseFloat(img.style.left); const startImgT = parseFloat(img.style.top);
                let currentCropLeft = parseFloat(container.dataset.cropLeftPx || 0);
                let currentCropTop = parseFloat(container.dataset.cropTopPx || 0);

                function onMouseMoveCropLine(event) {
                    let diffX = (event.clientX - startX) / nivelZoomActual;
                    let diffY = (event.clientY - startY) / nivelZoomActual;

                    if (lado === 'l') {
                        let maxDiff = startWidth - 20; if (diffX > maxDiff) diffX = maxDiff;
                        if (diffX < -currentCropLeft) diffX = -currentCropLeft;
                        container.style.width = (startWidth - diffX) + 'px'; container.style.left = (startLeft + diffX) + 'px';
                        img.style.left = (startImgL - diffX) + 'px'; container.dataset.cropLeftPx = currentCropLeft + diffX;
                    }
                    if (lado === 'r') {
                        let maxDiff = startWidth - 20; if (diffX < -maxDiff) diffX = -maxDiff;
                        container.style.width = (startWidth + diffX) + 'px';
                    }
                    if (lado === 't') {
                        let maxDiff = startHeight - 20; if (diffY > maxDiff) diffY = maxDiff;
                        if (diffY < -currentCropTop) diffY = -currentCropTop;
                        container.style.height = (startHeight - diffY) + 'px'; container.style.top = (startTop + diffY) + 'px';
                        img.style.top = (startImgT - diffY) + 'px'; container.dataset.cropTopPx = currentCropTop + diffY;
                    }
                    if (lado === 'b') {
                        let maxDiff = startHeight - 20; if (diffY < -maxDiff) diffY = -maxDiff;
                        container.style.height = (startHeight + diffY) + 'px';
                    }
                    if (container === elementoSeleccionado) actualizarInputsNumericos(container);
                    reposicionarMenuGlobal();
                }
                document.addEventListener('mousemove', onMouseMoveCropLine);
                document.addEventListener('mouseup', function() {
                    document.removeEventListener('mousemove', onMouseMoveCropLine);
                }, { once: true });
            });
        });
    }

    document.getElementById('g-btn-crop').addEventListener('click', function(e) {
        e.stopPropagation();
        if (!elementoSeleccionado) return;
        elementoSeleccionado.classList.toggle('mode-cropping');
        actualizarInputsNumericos(elementoSeleccionado);
    });

    document.getElementById('g-btn-rotate').addEventListener('click', function(e) {
        e.stopPropagation();
        if (!elementoSeleccionado) return;
        const img = elementoSeleccionado.querySelector('img');
        let currentRotation = parseInt(elementoSeleccionado.dataset.rotation || "0");
        currentRotation = (currentRotation + 90) % 360;
        elementoSeleccionado.dataset.rotation = currentRotation;
        img.style.transform = `rotate(${currentRotation}deg)`;
    });

    document.getElementById('g-btn-delete').addEventListener('click', function(e) {
        e.stopPropagation();
        if (!elementoSeleccionado) return;
        const padre = elementoSeleccionado.parentElement;
        elementoSeleccionado.remove();
        elementoSeleccionado = null;
        reposicionarMenuGlobal();
        if (padre && padre.classList.contains('paper-page')) {
            seleccionarHojaDestino(padre);
            acomodarImagenesEnHojaActiva();
        }
    });

    document.querySelector('#global-tools-menu .ancho-num').addEventListener('input', function() {
        if (this.value && elementoSeleccionado) {
            let nw = parseFloat(this.value) * CM_A_PX;
            let ratio = nw / elementoSeleccionado.offsetWidth;
            elementoSeleccionado.style.width = nw + 'px';
            const img = elementoSeleccionado.querySelector('img');
            img.style.width = (parseFloat(img.style.width) * ratio) + 'px';
            img.style.left = (parseFloat(img.style.left) * ratio) + 'px';
            elementoSeleccionado.dataset.cropLeftPx = (parseFloat(elementoSeleccionado.dataset.cropLeftPx) * ratio);
            reposicionarMenuGlobal();
        }
    });

    document.querySelector('#global-tools-menu .alto-num').addEventListener('input', function() {
        if (this.value && elementoSeleccionado) {
            let nh = parseFloat(this.value) * CM_A_PX;
            let ratio = nh / elementoSeleccionado.offsetHeight;
            elementoSeleccionado.style.height = nh + 'px';
            const img = elementoSeleccionado.querySelector('img');
            img.style.height = (parseFloat(img.style.height) * ratio) + 'px';
            img.style.top = (parseFloat(img.style.top) * ratio) + 'px';
            elementoSeleccionado.dataset.cropTopPx = (parseFloat(elementoSeleccionado.dataset.cropTopPx) * ratio);
            reposicionarMenuGlobal();
        }
    });

document.addEventListener('keydown', function(e) {
    // 1. FILTRO: Si el foco está en un campo de texto, no hacer nada más
    const esInput = e.target.closest('input') || e.target.closest('textarea') || e.target.isContentEditable;
    
    // --- ACCIONES QUE REQUIEREN CTRL/META ---
    if (e.ctrlKey || e.metaKey) {
        const tecla = e.key.toLowerCase();
        
        // Z - Deshacer
        if (tecla === 'z' && elementoSeleccionado) {
            e.preventDefault();
            deshacerUltimoRecorte(elementoSeleccionado);
            reposicionarMenuGlobal();
        }
        // C - Copiar
        else if (tecla === 'c' && elementoSeleccionado) {
            portapapeles = {
                src: elementoSeleccionado.querySelector('img').src,
                width: elementoSeleccionado.style.width,
                height: elementoSeleccionado.style.height,
                rotation: elementoSeleccionado.dataset.rotation || "0",
                cropLeft: elementoSeleccionado.dataset.cropLeftPx || "0",
                cropTop: elementoSeleccionado.dataset.cropTopPx || "0"
            };
        }
        // V - Pegar
        else if (tecla === 'v' && portapapeles) {
            e.preventDefault();
            agregarImagenCopiada(portapapeles);
        }
        return; // Salimos si usamos Ctrl
    }

    // --- ACCIONES DE TECLAS INDIVIDUALES (BORRAR) ---
    if (e.key === 'Delete' || e.key === 'Backspace') {
        if (esInput) return; // Si estamos escribiendo, NO borrar nada

        const seleccionados = document.querySelectorAll('.img-container.selected');
        if (seleccionados.length === 0) return;

        e.preventDefault();
        
        // Eliminamos todas las seleccionadas
        seleccionados.forEach(el => el.remove());
        
        // Limpiamos variables
        elementoSeleccionado = null;
        
        // Actualizamos UI
        if (typeof reposicionarMenuGlobal === 'function') reposicionarMenuGlobal();
        if (typeof acomodarImagenesEnHojaActiva === 'function') acomodarImagenesEnHojaActiva();
    }
});

document.getElementById('page-1').addEventListener('mousedown', function(e) {
    seleccionarHojaDestino(this);

    // .closest('.img-container') verifica si el clic fue en una imagen o dentro de ella
    // Si no fue en una imagen, deseleccionamos todo.
    if (!e.target.closest('.img-container')) {
        deseleccionarTodo();
    }
});



// Función específica para recrear la imagen con las propiedades guardadas
function agregarImagenCopiada(data) {
    imagenIdContador++;
    
    const container = document.createElement('div');
    container.className = 'img-container';
    container.id = 'img-box-' + imagenIdContador;
    
    // Aplicar tamaños y rotación guardados
    container.style.width = data.width;
    container.style.height = data.height;
    container.dataset.rotation = data.rotation;
    container.dataset.cropLeftPx = data.cropLeft;
    container.dataset.cropTopPx = data.cropTop;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'img-crop-wrapper';
    
    const img = document.createElement('img');
    img.src = data.src;
    img.style.width = data.width;
    img.style.height = data.height;
    
    wrapper.appendChild(img);
    container.appendChild(wrapper);

    // Agregar los elementos de control (resizers y líneas)
    agregarControlesAContenedor(container); 

    // Añadir a la hoja activa
    const destino = obtenerHojaActiva();
    destino.appendChild(container);

    hacerInteractiva(container);
    deseleccionarTodo();
    container.classList.add('selected');
    elementoSeleccionado = container;
    
    actualizarInputsNumericos(container);
    acomodarImagenesEnHojaActiva();
}

// Nota: Asegúrate de tener esta función auxiliar para no repetir código
function agregarControlesAContenedor(container) {
    const posiciones = ['tl', 'tm', 'tr', 'ml', 'mr', 'bl', 'bm', 'br'];
    posiciones.forEach(pos => {
        const resizer = document.createElement('div');
        resizer.className = `resizer ${pos}`;
        if (pos === 'tr') {
        resizer.innerHTML = '↻'; // El icono
        resizer.title = "Girar imagen";
    }
        container.appendChild(resizer);
    });

    const lineas = ['t', 'b', 'l', 'r'];
    lineas.forEach(l => {
        const lineEl = document.createElement('div');
        lineEl.className = `crop-line line-${l}`;
        container.appendChild(lineEl);
    });
}

function limpiarHojaActual() {
        // 1. Buscamos la hoja que tiene la clase 'active-page'
        const hojaActiva = document.querySelector('.paper-page.active-page');
        
        if (!hojaActiva) {
            Swal.fire('Atención', 'No hay ninguna hoja seleccionada.', 'info');
            return;
        }

        // 2. Buscamos cuántas imágenes hay para informar al usuario
        const imagenes = hojaActiva.querySelectorAll('.img-container');
        
        if (imagenes.length === 0) {
            Swal.fire('Info', 'La hoja ya está vacía.', 'info');
            return;
        }

        // 3. SweetAlert para confirmar el borrado masivo
        Swal.fire({
            title: '¿Limpiar esta hoja?',
            text: `Se eliminarán las ${imagenes.length} imágenes. Esta acción no se puede deshacer.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, borrar todo',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // 4. Eliminación efectiva: recorremos y borramos cada contenedor
                imagenes.forEach(img => img.remove());
                
                // 5. Limpiamos variables globales de selección para evitar errores
                deseleccionarTodo();
                
                Swal.fire('¡Hoja limpia!', 'Todas las imágenes han sido eliminadas.', 'success');
            }
        });
    }


function cerrarSistema() {
        if (confirm("¿Estás seguro de cerrar el sistema POS?")) {
            // Esto cierra la ventana del navegador
            window.close();
            // Opcional: podrías hacer un fetch('/shutdown') si configuraras una ruta especial en Flask
        }
    }

async function ejecutarQuitarFondo() {
    if (!elementoSeleccionado) return;
    const imgElement = elementoSeleccionado.querySelector('img');
    
    // Si no tenemos un respaldo, lo creamos ahora
    if (!elementoSeleccionado.dataset.originalSrc) {
        elementoSeleccionado.dataset.originalSrc = imgElement.src;
    }

    Swal.fire({ title: 'Procesando...', text: 'La IA está quitando el fondo...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

    try {
        const response = await fetch(imgElement.src);
        const blob = await response.blob();
        const formData = new FormData();
        formData.append('image', blob, 'img.png');

        const res = await fetch('/quitar-fondo', { method: 'POST', body: formData });
        const blobRes = await res.blob();
        imgElement.src = URL.createObjectURL(blobRes);
        Swal.close();
        
        // Avisar que se puede deshacer
        Swal.fire({ icon: 'success', title: 'Listo', text: 'Fondo eliminado. Si no te gusta, usa el botón "Deshacer"', timer: 2000 });
    } catch (err) {
        Swal.fire('Error', 'No se pudo procesar la imagen.', 'error');
    }
}

function deshacerCambios() {
    if (!elementoSeleccionado || !elementoSeleccionado.dataset.originalSrc) {
        Swal.fire('Aviso', 'No hay cambios para deshacer en esta imagen.', 'info');
        return;
    }
    const imgElement = elementoSeleccionado.querySelector('img');
    imgElement.src = elementoSeleccionado.dataset.originalSrc;
    // Opcional: limpiar el respaldo si quieres que solo sea un paso
    // delete elementoSeleccionado.dataset.originalSrc; 
}

function agregarNodoRotacion(contenedor) {
    // Si ya existe el nodo, no lo agregamos otra vez
    if (contenedor.querySelector('.rotate-handle')) return;

    const handle = document.createElement('div');
    handle.className = 'rotate-handle';
    contenedor.appendChild(handle);

    handle.addEventListener('mousedown', (e) => {
        e.stopPropagation(); // Evita que la imagen se mueva al arrastrar el nodo
        
        const rect = contenedor.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        function onMouseMove(event) {
            const dx = event.clientX - centerX;
            const dy = event.clientY - centerY;
            // Calculamos el ángulo
            const angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90;
            contenedor.dataset.rotation = angle;
            contenedor.style.transform = `rotate(${angle}deg)`;
            reposicionarMenuGlobal();
        }

        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });
}

function iniciarRotacion(container, e) {
    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    function onMouseMove(event) {
        const dx = event.clientX - centerX;
        const dy = event.clientY - centerY;
        // Calculamos el ángulo
        const angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90;
        
        container.style.transform = `rotate(${angle}deg)`;
        container.dataset.rotation = angle;
        reposicionarMenuGlobal();
    }

    function onMouseUp() {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    }

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
}

async function ejecutarPegadoManual() {
    try {
        // Pedimos acceso al portapapeles
        const clipboardItems = await navigator.clipboard.read();
        
        for (const item of clipboardItems) {
            if (item.types.includes('image/png') || item.types.includes('image/jpeg')) {
                const blob = await item.getType(item.types[0]);
                
                // Convertimos el blob a una URL que podamos usar
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Llamamos a la misma función que usas para el CTRL+V
                    agregarImagenCopiada(e.target.result); 
                };
                reader.readAsDataURL(blob);
                return; // Salimos al encontrar la imagen
            }
        }
        Swal.fire('Aviso', 'No se encontró una imagen en el portapapeles.', 'info');
    } catch (err) {
        console.error('Error al acceder al portapapeles:', err);
        Swal.fire({
            icon: 'error',
            title: 'Acceso denegado',
            text: 'El navegador bloqueó el pegado automático. Por favor, usa Ctrl+V o da permisos de portapapeles en tu navegador.'
        });
    }
}


function traerAlFrente() {
    if (!elementoSeleccionado) return;
    
    // Obtenemos el z-index más alto de todos los elementos
    const todos = document.querySelectorAll('.img-container');
    let maxZ = 10; // Empezamos desde nuestra base
    todos.forEach(el => {
        let z = parseInt(window.getComputedStyle(el).zIndex) || 0;
        if (z > maxZ) maxZ = z;
    });
    
    elementoSeleccionado.style.zIndex = maxZ + 1;
}

function enviarAlFondo() {
    if (!elementoSeleccionado) return;
    
    // Obtenemos el z-index más bajo de todos los elementos
    const todos = document.querySelectorAll('.img-container');
    let minZ = 10; // Nuestra base
    
    // Asignamos el valor mínimo actual menos 1, pero sin bajar de 10
    elementoSeleccionado.style.zIndex = minZ; 
    
    // Opcional: Si quieres que realmente se "hunda", 
    // puedes recorrer todos los demás y subirlos un nivel:
    todos.forEach(el => {
        if (el !== elementoSeleccionado) {
            let z = parseInt(window.getComputedStyle(el).zIndex) || 10;
            el.style.zIndex = z + 1;
        }
    });
}

function aplicarSnapping(x, y, elActual) {
    const umbral = 10; // Pixeles de atracción
    let snappedX = x;
    let snappedY = y;

    // 1. Snapping contra los bordes de la hoja (padreRect)
    if (x < umbral) snappedX = 0;
    if (y < umbral) snappedY = 0;

    // 2. Snapping contra otras imágenes
    document.querySelectorAll('.img-container').forEach(otra => {
        if (otra === elActual) return;
        
        const rect = otra.getBoundingClientRect();
        // Si la distancia entre la imagen actual y otra es menor al umbral
        // "jalamos" la posición de la actual hacia la posición de la otra
        if (Math.abs(x - rect.left) < umbral) snappedX = rect.left;
        if (Math.abs(y - rect.top) < umbral) snappedY = rect.top;
    });

    return { x: snappedX, y: snappedY };
}


// Aplica estilos de comando (Negrita, Color, etc.)
function formatoTexto(comando, valor = null) {
    document.execCommand(comando, false, valor);
}

// Cambia el tamaño real en píxeles
function cambiarTamanio(delta) {
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    
    // Obtiene el elemento que contiene el texto seleccionado
    const elemento = sel.anchorNode.parentElement;
    const estiloActual = window.getComputedStyle(elemento).fontSize;
    const nuevoTamanio = parseInt(estiloActual) + delta;
    
    elemento.style.fontSize = nuevoTamanio + "px";
}



function crearCuadroTexto() {
    const nuevoDiv = document.createElement('div');
    // 'img-container' mantiene tu lógica global, 'text-container' aplica el CSS exclusivo
    nuevoDiv.className = 'img-container text-container selected'; 
    nuevoDiv.style.width = '200px';
    nuevoDiv.style.minHeight = '50px';
    nuevoDiv.style.left = '100px';
    nuevoDiv.style.top = '100px';
    
    nuevoDiv.innerHTML = `
        <div class="texto-editable" contenteditable="true" style="width:100%; height:100%;">
            Escribe aquí...
        </div>
        <div class="resizer"></div>
    `;

    document.getElementById('page-1').appendChild(nuevoDiv);
    
    // Aquí es CRÍTICO: Usar una función que no toque tus imágenes
    hacerTextoInteractiva(nuevoDiv);
    
    elementoSeleccionado = nuevoDiv;
    reposicionarMenuGlobal();
}
    </script>

</body>
</html>
"""

# --- IMPORTS ---
from functools import wraps
from flask import Flask, render_template_string, request, send_file
import json
import io
from PIL import Image
from rembg import remove, new_session

app = Flask(__name__)

# --- SEGURIDAD (Tu código está perfecto aquí) ---
def verificar_acceso(email):
    try:
        with open('usuarios.json', 'r') as f:
            data = json.load(f)
            usuario_info = data.get(email)
            return usuario_info and usuario_info.get('activo') == True
    except:
        return False

def requerir_acceso(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = request.args.get('email')
        if not verificar_acceso(email):
            return "Acceso denegado. Contacta al administrador.", 403
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS ---
@app.route('/')
@requerir_acceso  # <--- PROTEGIDA
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/quitar-fondo', methods=['POST'])
@requerir_acceso  # <--- PROTEGIDA TAMBIÉN
def procesar_quitar_fondo():
    file = request.files['image']
    input_image = Image.open(file.stream)
    output_image = remove(input_image, session=session)
    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

# --- INICIALIZACIÓN ---
session = new_session(model_name="u2netp")

import os

if __name__ == '__main__':
    # Solo ejecutará esto en tu PC local, NO en Render
    app.run(debug=True)
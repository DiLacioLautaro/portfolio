# Portfolio de Lautaro Di Lacio

Sitio personal de **Lautaro Di Lacio**, Desarrollador Full Stack .NET con +3,5 años en desarrollo .NET (C#, .NET 8, SQL Server, Angular, TypeScript).

**Ver el sitio:** https://dilaciolautaro.github.io/portfolio/

[CV en PDF](https://dilaciolautaro.github.io/portfolio/CV-Lautaro-Di-Lacio.pdf) · [LinkedIn](https://www.linkedin.com/in/lautaro-di-lacio) · [GitHub](https://github.com/DiLacioLautaro)

## Qué hay en el sitio

- **Experiencia:** SWS Services (ERP web y app móvil para distribuidoras de agua y soda), Baufest para Cencosud (retail) y Voolkia para Mercado Libre.
- **Proyectos propios:** [SousChef](https://souschefvirtual.com), una plataforma en producción para reposteras con asistente de IA, y [Golden Classic](https://github.com/DiLacioLautaro/golden-classic), una plataforma de progreso físico y posing para culturismo clásico, en fase de pruebas.
- **Stack:** las tecnologías que manejo, filtrables por categoría y separadas en principales y complementarias.
- **Contacto** y descarga del CV.

## Cómo está hecho

HTML, CSS y JavaScript sin frameworks ni paso de build, en un solo archivo (`index.html`). Diseño en grilla tipo tablero, tema oscuro, adaptado a teléfono y escritorio.

| Ruta | Contenido |
|---|---|
| `index.html` | Todo el sitio: estructura, estilos y scripts |
| `CV-Lautaro-Di-Lacio.pdf` | CV descargable desde el sitio |
| `img/` | Foto y capturas de los proyectos |
| `video/` | Demo de SousChef |

## Verlo en local

No hace falta instalar nada: alcanza con abrir `index.html` en el navegador. Para servirlo igual que en producción:

```bash
python -m http.server 8000
```

## Publicación

Se publica con GitHub Pages desde la rama `main`. Cada push a `main` actualiza el sitio.

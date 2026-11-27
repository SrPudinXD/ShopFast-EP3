function generarGrafico(id, datos) {

    const contenedor = document.getElementById(id);
    contenedor.replaceChildren();

    if (!datos) {
        contenedor.textContent = "Datos no disponibles";
        return;
    }

    const elementos = Object.entries(datos);

    if (elementos.length === 0) {
        contenedor.textContent = "Sin interacciones registradas";
        return;
    }

    const maximo = Math.max(1, ...Object.values(datos));

    elementos.forEach(([nombre, cantidad]) => {

        const fila = document.createElement("div");
        fila.className = "fila-grafico";

        const etiqueta = document.createElement("div");
        etiqueta.className = "etiqueta-grafico";

        const titulo = document.createElement("span");
        titulo.textContent = nombre;

        const valor = document.createElement("strong");
        valor.textContent = cantidad;

        etiqueta.append(titulo, valor);

        const fondo = document.createElement("div");
        fondo.className = "barra-fondo";

        const barra = document.createElement("div");
        barra.className = "barra-valor";
        barra.style.width = (cantidad / maximo * 100) + "%";

        fondo.appendChild(barra);
        fila.append(etiqueta, fondo);
        contenedor.appendChild(fila);
    });
}


async function actualizarDashboard() {

    try {

        const respuesta = await fetch("/api/dashboard", {
            cache: "no-store"
        });

        if (!respuesta.ok) {
            throw new Error("Error de conexion");
        }

        const datos = await respuesta.json();

        document.getElementById("eventos").textContent =
            datos.eventos_registrados ?? "No disponible";

        document.getElementById("redis").textContent =
            datos.redis ? "Operativo" : "Inactivo";

        document.getElementById("modelo").textContent =
            datos.modelo_configurado;

        document.getElementById("entorno").textContent =
            datos.entorno;

        document.getElementById("dashboard").textContent =
            datos.dashboard;

        document.getElementById("dashboard").className =
            "activo";

        document.getElementById("estado-redis").textContent =
            datos.redis ? "Conectado" : "Desconectado";

        document.getElementById("estado-redis").className =
            datos.redis ? "activo" : "inactivo";

        document.getElementById("inventario").textContent =
            datos.inventario;

        const eventos = datos.distribucion_eventos;

        generarGrafico("grafico-eventos", eventos ? {
            "Clicks": eventos.click,
            "Impresiones": eventos.impression,
            "Carrito": eventos.cart,
            "Compras": eventos.purchase
        } : null);

        generarGrafico(
            "grafico-productos",
            datos.interacciones_productos
        );

        document.getElementById("actualizacion").textContent =
            "Ultima actualizacion: " +
            new Date(datos.actualizacion).toLocaleString("es-CL", {
                timeZone: "America/Santiago"
            });

    } catch (error) {

        console.error(error);

        ["eventos", "redis", "modelo", "entorno",
         "estado-redis", "inventario"].forEach(id => {
            document.getElementById(id).textContent = "--";
        });

        document.getElementById("dashboard").textContent =
            "Sin conexion";

        document.getElementById("dashboard").className =
            "inactivo";

        generarGrafico("grafico-eventos", null);
        generarGrafico("grafico-productos", null);

        document.getElementById("actualizacion").textContent =
            "Error al actualizar los indicadores";
    }
}

actualizarDashboard();

setInterval(actualizarDashboard, 10000);

// Recomendaciones del Dashboard V3
async function consultarRecomendaciones() {
    const panel = document.getElementById("ia-productos");
    const boton = document.getElementById("btn-recomendaciones");

    boton.disabled = true;
    panel.textContent = "Consultando modelo...";

    try {
        const respuesta = await fetch("/api/recomendaciones", {
            cache: "no-store"
        });

        if (!respuesta.ok) {
            throw new Error("Motor no disponible");
        }

        const datos = await respuesta.json();

        document.getElementById("ia-version").textContent =
            datos.model_version ?? "Sin modelo";

        document.getElementById("ia-entorno").textContent =
            datos.inference_environment;

        document.getElementById("ia-fallback").textContent =
            datos.fallback ? "Activo" : "Inactivo";

        document.getElementById("ia-inventario").textContent =
            datos.inventory_environment;

        document.getElementById("ia-id").textContent =
            datos.recommendation_id;

        panel.replaceChildren();

        for (const item of datos.items) {
            const fila = document.createElement("p");

            fila.textContent =
                item.product_id + " | Score: " +
                Number(item.score).toFixed(6);

            panel.appendChild(fila);
        }

        if (!datos.items.length) {
            panel.textContent =
                "Sin productos con inventario elegible y vigente.";
        }

        const detalle = document.createElement("p");
        detalle.textContent =
            "Latencia: " + datos.latencia_ms + " ms";

        panel.appendChild(detalle);

        const exclusiones = document.createElement("p");
        exclusiones.textContent =
            "Exclusiones: " + JSON.stringify(datos.excluded);

        panel.appendChild(exclusiones);

    } catch (error) {
        panel.textContent = "Error al consultar recomendaciones";

        for (const id of ["ia-version", "ia-entorno",
                          "ia-fallback", "ia-inventario", "ia-id"]) {
            document.getElementById(id).textContent = "--";
        }
    } finally {
        boton.disabled = false;
    }
}

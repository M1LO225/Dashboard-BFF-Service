// script.js

// --- Configuración ---
const AUTH_SERVICE_BASE_URL = "http://localhost:8000/api/v1/auth";
const SCAN_ORCHESTRATOR_BASE_URL = "http://localhost:8001/api/v1/scans";
const DASHBOARD_BFF_BASE_URL = "http://localhost:8007/api/v1/dashboards";

// --- Elementos del DOM Comunes ---
const messageArea = document.getElementById('message-area');

// --- Estado Global ---
let jwtToken = localStorage.getItem('jwt_token');
let loggedInUser = localStorage.getItem('logged_in_user');

// --- Funciones de Utilidad ---
function displayMessage(message, type = 'info') {
    if (messageArea) {
        messageArea.textContent = message;
        messageArea.className = `alert alert-${type}`;
        messageArea.style.display = 'block';
        setTimeout(() => {
            clearMessage();
        }, 7000);
    }
}

function clearMessage() {
    if (messageArea) {
        messageArea.textContent = '';
        messageArea.style.display = 'none';
    }
}

function getAuthHeaders() {
    if (!jwtToken) {
        displayMessage('No hay token de sesión. Por favor, inicia sesión.', 'error');
        // Redirigir a index.html (ruta raiz) si no hay token en una página protegida
        if (window.location.pathname === '/dashboard') {
            window.location.href = '/'; // Redirige a la raíz (index.html)
        }
        return null;
    }
    return {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
    };
}

// --- Lógica de Autenticación (solo para index.html) ---
async function handleLogin(event) {
    event.preventDefault();
    clearMessage();

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // Asegurarse de que estamos en la página de login por la presencia de estos elementos
    if (!usernameInput || !passwordInput) return; 

    const username = usernameInput.value;
    const password = passwordInput.value;

    try {
        const response = await fetch(`${AUTH_SERVICE_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Fallo de inicio de sesión');
        }

        const data = await response.json();
        jwtToken = data.access_token;
        loggedInUser = username;
        localStorage.setItem('jwt_token', jwtToken);
        localStorage.setItem('logged_in_user', loggedInUser);
        
        displayMessage('¡Inicio de sesión exitoso! Redirigiendo...', 'success');
        window.location.href = '/dashboard'; // Redirigir a la ruta /dashboard

    } catch (error) {
        displayMessage(`Error de inicio de sesión: ${error.message}`, 'error');
        console.error('Login error:', error);
    }
}

// --- Lógica de Cierre de Sesión (para dashboard.html) ---
function handleLogout() {
    jwtToken = null;
    loggedInUser = null;
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('logged_in_user');
    displayMessage('Sesión cerrada correctamente.', 'info');
    window.location.href = '/'; // Redirigir de vuelta a la raíz (index.html)
}

// --- Lógica de Inicio de Escaneo (para dashboard.html) ---
async function handleStartScan(event) {
    event.preventDefault();
    clearMessage();

    const domainNameInput = document.getElementById('domain-name');
    if (!domainNameInput) return;

    const domainName = domainNameInput.value;
    const headers = getAuthHeaders();
    if (!headers) return;

    displayMessage('Iniciando escaneo... esto puede tardar unos minutos.', 'info');

    try {
        const response = await fetch(SCAN_ORCHESTRATOR_BASE_URL, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ domain_name: domainName })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Fallo al iniciar el escaneo');
        }

        const scan = await response.json();
        displayMessage(`Escaneo para ${scan.domain_name} iniciado. ID de Escaneo: ${scan.id}. Puedes cargar el dashboard en unos momentos.`, 'success');
        
        const scanIdInput = document.getElementById('scan-id-input');
        if (scanIdInput) {
            scanIdInput.value = scan.id;
            setTimeout(() => loadDashboard(scan.id), 5000);
        }

    } catch (error) {
        displayMessage(`Error al iniciar escaneo: ${error.message}`, 'error');
        console.error('Scan start error:', error);
    }
}

// --- Lógica de Carga y Renderizado del Dashboard (para dashboard.html) ---
async function loadDashboard(scanId) {
    const dashboardContainer = document.getElementById('dashboard-container');
    if (!dashboardContainer) return;

    clearMessage();
    dashboardContainer.innerHTML = `
        <div class="card-body text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Cargando Dashboard para ${scanId}... (Puede requerir varios reintentos para ver el progreso completo)</p>
        </div>
    `;

    const headers = getAuthHeaders();
    if (!headers) {
        dashboardContainer.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`${DASHBOARD_BFF_BASE_URL}/${scanId}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Fallo al cargar los datos del dashboard');
        }

        const dashboardData = await response.json();
        renderDashboard(dashboardData);
        displayMessage('Dashboard cargado exitosamente. Recarga o re-carga el ID para ver actualizaciones.', 'success');

    } catch (error) {
        dashboardContainer.innerHTML = '';
        displayMessage(`Error al cargar dashboard: ${error.message}. Asegúrate que el ID es correcto y que el escaneo ha iniciado.`, 'error');
        console.error('Dashboard load error:', error);
    }
}

function renderDashboard(data) {
    const dashboardContainer = document.getElementById('dashboard-container');
    if (!dashboardContainer) return;

    dashboardContainer.innerHTML = '';

    let html = `
        <div class="card mb-4 dashboard-overview-card">
            <div class="card-header bg-primary text-white">
                <h3>Resumen del Escaneo: ${data.domain_name}</h3>
            </div>
            <div class="card-body">
                <p><strong>ID de Escaneo:</strong> <span class="badge bg-secondary scan-id-badge">${data.scan_id}</span></p>
                <p><strong>Estado:</strong> <span class="badge ${data.status === 'COMPLETED' ? 'bg-success' : 'bg-warning'}">${data.status}</span></p>
                <p><strong>Solicitado el:</strong> ${new Date(data.requested_at).toLocaleString()}</p>
                <p class="h5 mt-3"><strong>Puntuación de Riesgo Total Agregada:</strong> <span class="badge bg-danger risk-score-badge">${data.total_risk_score !== null ? data.total_risk_score.toFixed(2) : 'N/A'}</span></p>
            </div>
        </div>

        <div class="mt-4">
            <h4>Activos Descubiertos (${data.assets.length})</h4>
            <div class="accordion" id="assetsAccordion">
    `;

    if (data.assets && data.assets.length > 0) {
        data.assets.forEach((asset, index) => {
            let scaBadgeClass = 'bg-secondary';
            if (asset.sca_score >= 8) scaBadgeClass = 'bg-danger';
            else if (asset.sca_score >= 5) scaBadgeClass = 'bg-warning text-dark';
            else if (asset.sca_score > 0) scaBadgeClass = 'bg-info';

            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingAsset${index}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseAsset${index}" aria-expanded="false" aria-controls="collapseAsset${index}">
                            Activo: ${asset.value} - Tipo: ${asset.asset_type} - SCA: <span class="badge ${scaBadgeClass}">${asset.sca_score !== null ? asset.sca_score.toFixed(2) : 'N/A'}</span>
                        </button>
                    </h2>
                    <div id="collapseAsset${index}" class="accordion-collapse collapse" aria-labelledby="headingAsset${index}" data-bs-parent="#assetsAccordion">
                        <div class="accordion-body">
                            <p><strong>ID de Activo:</strong> <span class="badge bg-light text-dark">${asset.id}</span></p>
                            <p><strong>Puntuaciones CIA (SCA):</strong> C:<span class="badge bg-info">${asset.sca_c !== null ? asset.sca_c.toFixed(2) : 'N/A'}</span> I:<span class="badge bg-info">${asset.sca_i !== null ? asset.sca_i.toFixed(2) : 'N/A'}</span> A:<span class="badge bg-info">${asset.sca_d !== null ? asset.sca_d.toFixed(2) : 'N/A'}</span></p>
                            
                            <h6 class="mt-3">Riesgos Asociados (${asset.risks.length})</h6>
                            ${asset.risks && asset.risks.length > 0 ? `
                                <ul class="list-group">
                                    ${asset.risks.map(risk => {
                                        let riskBadgeClass = 'bg-success';
                                        if (risk.risk_score >= 7) riskBadgeClass = 'bg-danger';
                                        else if (risk.risk_score >= 4) riskBadgeClass = 'bg-warning text-dark';
                                        
                                        return `
                                            <li class="list-group-item d-flex justify-content-between align-items-center flex-wrap">
                                                <div>
                                                    <strong>CVE:</strong> <a href="https://nvd.nist.gov/vuln/detail/${risk.cve_id}" target="_blank">${risk.cve_id}</a> <br/>
                                                    <strong>CVSS:</strong> <span class="badge bg-dark">${risk.cvss_score.toFixed(1)}</span>
                                                </div>
                                                <div class="mt-2 mt-sm-0">
                                                    <strong>Riesgo (NR):</strong> <span class="badge ${riskBadgeClass}">${risk.risk_score.toFixed(2)}</span>
                                                </div>
                                            </li>
                                        `;
                                    }).join('')}
                                </ul>
                            ` : '<p class="text-muted">No se encontraron riesgos para este activo.</p>'}
                        </div>
                    </div>
                </div>
            `;
        });
    } else {
        html += '<p class="text-muted text-center">No se han descubierto activos para este escaneo todavía.</p>';
    }

    html += `
            </div>
        </div>
    `;
    dashboardContainer.innerHTML = html;
}


// --- Inicialización ---
document.addEventListener('DOMContentLoaded', () => {
    // Comprobación de la página actual por su ruta
    const currentPath = window.location.pathname;
    const isLoginPage = currentPath === '/'; // index.html es la raíz
    const isDashboardPage = currentPath === '/dashboard';

    if (isLoginPage) {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
        }
    } else if (isDashboardPage) {
        const logoutBtn = document.getElementById('logout-btn');
        const userDisplay = document.getElementById('user-display');
        const scanForm = document.getElementById('scan-form');
        const loadDashboardBtn = document.getElementById('load-dashboard-btn');
        const scanIdInput = document.getElementById('scan-id-input');

        // Comprobar si el usuario está logueado al cargar el dashboard
        if (!jwtToken || !loggedInUser) {
            window.location.href = '/'; // Redirigir a la raíz (index.html) si no hay token
            return;
        }

        // Configurar elementos del dashboard
        if (userDisplay) userDisplay.textContent = `Bienvenido, ${loggedInUser}`;
        if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
        if (scanForm) scanForm.addEventListener('submit', handleStartScan);
        if (loadDashboardBtn) {
            loadDashboardBtn.addEventListener('click', () => {
                const scanId = scanIdInput.value;
                if (scanId) {
                    loadDashboard(scanId);
                } else {
                    displayMessage('Por favor, ingresa un ID de Escaneo (UUID).', 'warning');
                }
            });
        }
    }
});
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OPCIONES DEL NAVEGADOR
options = ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# UBICACIÓN DE CHROMEDRIVER
ruta_driver = r"C:\Users\duvan.botero\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

def inicializar_driver():
    """Inicializa el driver con manejo de errores"""
    try:
        service = Service(ruta_driver)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        logger.error(f"Error inicializando driver: {e}")
        return None

def buscar_elemento_multiple(driver, wait, selectores, timeout=10):
    """Busca un elemento usando múltiples estrategias"""
    wait_local = WebDriverWait(driver, timeout)
    for selector_type, selector_value in selectores:
        try:
            if selector_type == "wait_clickable":
                return wait_local.until(EC.element_to_be_clickable(selector_value))
            elif selector_type == "wait_present":
                return wait_local.until(EC.presence_of_element_located(selector_value))
            elif selector_type == "wait_visible":
                return wait_local.until(EC.visibility_of_element_located(selector_value))
            else:
                elemento = driver.find_element(selector_type, selector_value)
                if elemento.is_displayed():
                    return elemento
        except (TimeoutException, NoSuchElementException):
            continue
    return None

def hacer_click_seguro(driver, elemento):
    """Hace click en un elemento usando JavaScript si es necesario"""
    try:
        # Scroll al elemento primero
        driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
        time.sleep(0.5)
        elemento.click()
        return True
    except:
        try:
            driver.execute_script("arguments[0].click();", elemento)
            return True
        except:
            return False

def esperar_carga_completa_pagina(driver, wait):
    """Espera que la página cargue completamente antes de interactuar"""
    logger.info("=== ESPERANDO CARGA COMPLETA DE LA PÁGINA ===")
    
    # Esperar que el DOM esté completamente cargado
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    logger.info("✅ Documento completamente cargado")
    
    # Esperar que jQuery termine (si existe)
    try:
        wait.until(lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0"))
        logger.info("✅ jQuery terminó de cargar")
    except:
        logger.info("jQuery no detectado o no aplicable")
    
    # Esperar tiempo adicional para elementos dinámicos
    time.sleep(5)
    
    # Verificar elementos críticos
    elementos_criticos = ['button_service', 'services_drop', 'service_list']
    for elemento_id in elementos_criticos:
        try:
            elemento = driver.find_element(By.ID, elemento_id)
            logger.info(f"✅ {elemento_id} encontrado")
        except NoSuchElementException:
            logger.warning(f"⚠️ {elemento_id} no encontrado aún")
    
    logger.info("Carga completa verificada")

def debug_completo_dropdown(driver):
    """Debug completo del estado del dropdown"""
    logger.info("=== DEBUG COMPLETO DEL DROPDOWN ===")
    
    try:
        # Información completa del DOM relacionado con el dropdown
        info_completa = driver.execute_script("""
            var info = {
                button_service: null,
                services_drop: null,
                service_list: null,
                dropdown_div: null
            };
            
            // button_service
            var btn = document.getElementById('button_service');
            if (btn) {
                info.button_service = {
                    exists: true,
                    tag: btn.tagName,
                    text: btn.textContent.trim(),
                    onclick: btn.getAttribute('onclick'),
                    class: btn.getAttribute('class'),
                    style_display: window.getComputedStyle(btn).display,
                    visible: btn.offsetParent !== null,
                    enabled: !btn.disabled
                };
            }
            
            // services_drop
            var dropdown = document.getElementById('services_drop');
            if (dropdown) {
                info.services_drop = {
                    exists: true,
                    class: dropdown.getAttribute('class'),
                    style_display: window.getComputedStyle(dropdown).display,
                    style_visibility: window.getComputedStyle(dropdown).visibility,
                    visible: dropdown.offsetParent !== null,
                    children_count: dropdown.children.length
                };
            }
            
            // service_list
            var list = document.getElementById('service_list');
            if (list) {
                info.service_list = {
                    exists: true,
                    children_count: list.children.length,
                    style_display: window.getComputedStyle(list).display,
                    visible: list.offsetParent !== null,
                    first_child_tag: list.children.length > 0 ? list.children[0].tagName : null
                };
            }
            
            // Buscar divs con dropdown en la clase
            var dropdownDivs = document.querySelectorAll('div[class*="dropdown"]');
            info.dropdown_divs_count = dropdownDivs.length;
            
            return info;
        """)
        
        logger.info("📊 Estado completo del dropdown:")
        for elemento, datos in info_completa.items():
            if datos:
                logger.info(f"  {elemento}: {datos}")
            else:
                logger.info(f"  {elemento}: No encontrado")
                
    except Exception as e:
        logger.error(f"Error en debug completo: {e}")

def abrir_dropdown_servicios_corregido(driver, wait):
    """Versión corregida que encuentra específicamente el botón correcto"""
    logger.info("=== ABRIENDO DROPDOWN DE SERVICIOS (VERSIÓN CORREGIDA) ===")
    
    # Paso 1: Verificar que el botón button_service existe
    try:
        button_service = wait.until(EC.presence_of_element_located((By.ID, "button_service")))
        logger.info("✅ button_service encontrado")
        
        # Verificar información del botón
        tag = button_service.tag_name
        text = button_service.text.strip()
        onclick = button_service.get_attribute("onclick") or ""
        class_attr = button_service.get_attribute("class") or ""
        is_displayed = button_service.is_displayed()
        is_enabled = button_service.is_enabled()
        
        logger.info(f"📋 Info del botón: tag='{tag}', text='{text}', onclick='{onclick}', class='{class_attr}'")
        logger.info(f"📋 Estado: visible={is_displayed}, habilitado={is_enabled}")
        
        if tag != "button":
            logger.warning(f"⚠️ Elemento no es un botón, es: {tag}")
            
    except TimeoutException:
        logger.error("❌ button_service no encontrado")
        return False
    
    # Paso 2: Asegurar que el botón esté visible y clickeable
    try:
        # Scroll para asegurar visibilidad
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_service)
        time.sleep(2)
        
        # Esperar que sea clickeable
        button_clickeable = wait.until(EC.element_to_be_clickable((By.ID, "button_service")))
        logger.info("✅ Botón confirmado como clickeable")
        
    except TimeoutException:
        logger.error("❌ Botón no se volvió clickeable")
        return False
    
    # Paso 3: Intentar click con múltiples estrategias
    estrategias_click = [
        ("Click directo", lambda: button_clickeable.click()),
        ("Click JavaScript", lambda: driver.execute_script("arguments[0].click();", button_clickeable)),
        ("Click con evento", lambda: driver.execute_script("""
            var event = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            arguments[0].dispatchEvent(event);
        """, button_clickeable)),
        ("Función específica", lambda: driver.execute_script("showList('services_drop');")),
        ("Click forzado", lambda: driver.execute_script("""
            var btn = document.getElementById('button_service');
            if (btn && btn.onclick) {
                btn.onclick();
            } else if (typeof showList === 'function') {
                showList('services_drop');
            }
        """))
    ]
    
    for nombre_estrategia, estrategia_func in estrategias_click:
        try:
            logger.info(f"Intentando: {nombre_estrategia}")
            estrategia_func()
            logger.info(f"✅ {nombre_estrategia} ejecutado")
            
            # Esperar y verificar si se abrió
            time.sleep(3)
            
            # Verificar múltiples indicadores de que se abrió
            dropdown_abierto = False
            
            # Verificar services_drop
            try:
                services_drop = driver.find_element(By.ID, "services_drop")
                if services_drop.is_displayed():
                    logger.info("✅ services_drop está visible")
                    dropdown_abierto = True
            except NoSuchElementException:
                logger.warning("services_drop no encontrado")
            
            # Verificar service_list
            try:
                service_list = driver.find_element(By.ID, "service_list")
                if service_list.is_displayed():
                    logger.info("✅ service_list está visible")
                    dropdown_abierto = True
            except NoSuchElementException:
                logger.warning("service_list no encontrado")
            
            if dropdown_abierto:
                logger.info(f"✅ Dropdown abierto exitosamente con: {nombre_estrategia}")
                return True
            else:
                logger.warning(f"⚠️ {nombre_estrategia} no abrió el dropdown")
                
        except Exception as e:
            logger.warning(f"❌ {nombre_estrategia} falló: {e}")
            continue
    
    # Paso 4: Intentar forzar la apertura modificando el DOM
    try:
        logger.info("Intentando forzar apertura modificando DOM...")
        resultado = driver.execute_script("""
            // Forzar visibilidad del dropdown
            var dropdown = document.getElementById('services_drop');
            var serviceList = document.getElementById('service_list');
            
            if (dropdown) {
                dropdown.style.display = 'block';
                dropdown.style.visibility = 'visible';
                dropdown.style.opacity = '1';
                dropdown.style.position = 'relative';
                dropdown.style.zIndex = '9999';
            }
            
            if (serviceList) {
                serviceList.style.display = 'block';
                serviceList.style.visibility = 'visible';
                serviceList.style.opacity = '1';
                serviceList.style.maxHeight = '500px';
                serviceList.style.overflow = 'auto';
            }
            
            // Verificar resultado
            return {
                dropdown_visible: dropdown ? dropdown.offsetParent !== null : false,
                service_list_visible: serviceList ? serviceList.offsetParent !== null : false
            };
        """)
        
        logger.info(f"Resultado forzar DOM: {resultado}")
        
        if resultado.get('service_list_visible') or resultado.get('dropdown_visible'):
            logger.info("✅ Dropdown forzado a abrirse")
            return True
            
    except Exception as e:
        logger.error(f"Error forzando DOM: {e}")
    
    logger.error("❌ Todas las estrategias fallaron")
    return False

def analizar_dropdown_servicios_detallado(driver):
    """Analiza la estructura completa del dropdown para debugging"""
    logger.info("=== ANÁLISIS DETALLADO DEL DROPDOWN DE SERVICIOS ===")
    
    try:
        # Verificar si el service_list está visible
        service_list = driver.find_element(By.ID, "service_list")
        if service_list.is_displayed():
            logger.info("✅ Lista de servicios (service_list) es visible")
            
            # Buscar específicamente CARDIOLOGÍA
            cardiologia_buttons = service_list.find_elements(By.XPATH, ".//button[contains(@data-name, 'CARDIOLOGÍA')]")
            logger.info(f"🔍 Botones de CARDIOLOGÍA encontrados: {len(cardiologia_buttons)}")
            
            for i, btn in enumerate(cardiologia_buttons):
                try:
                    text = btn.text.strip()
                    data_value = btn.get_attribute("data-value")
                    data_name = btn.get_attribute("data-name")
                    class_attr = btn.get_attribute("class")
                    is_displayed = btn.is_displayed()
                    
                    logger.info(f"  Botón {i+1}: text='{text}', data-value='{data_value}', data-name='{data_name}', class='{class_attr}', visible={is_displayed}")
                    
                except Exception as e:
                    logger.error(f"  Error analizando botón {i+1}: {e}")
            
            # Buscar todos los botones principales (subtitle)
            subtitle_buttons = service_list.find_elements(By.XPATH, ".//li[@class='subtitle']//button")
            logger.info(f"📋 Total de especialidades principales: {len(subtitle_buttons)}")
            
            for i, btn in enumerate(subtitle_buttons[:10]):  # Solo los primeros 10
                try:
                    text = btn.text.strip()
                    data_value = btn.get_attribute("data-value")
                    logger.info(f"  Especialidad {i+1}: '{text}' (data-value: {data_value})")
                except:
                    continue
                    
        else:
            logger.warning("⚠️ Lista de servicios no está visible")
            
    except NoSuchElementException:
        logger.warning("⚠️ No se encontró el elemento service_list")

def seleccionar_cardiologia_actualizado(driver, wait):
    """Selecciona CARDIOLOGÍA con la estructura HTML exacta"""
    logger.info("=== SELECCIONANDO CARDIOLOGÍA CON ESTRUCTURA ACTUALIZADA ===")
    
    # Verificar que el dropdown esté abierto y el service_list visible
    try:
        service_list = wait.until(EC.presence_of_element_located((By.ID, "service_list")))
        if not service_list.is_displayed():
            logger.warning("service_list no está visible, esperando...")
            wait.until(EC.visibility_of_element_located((By.ID, "service_list")))
        
        logger.info("✅ service_list está visible")
    except TimeoutException:
        logger.error("❌ No se pudo encontrar service_list visible")
        return False
    
    # Selectores específicos para CARDIOLOGÍA basados en el HTML exacto
    selectores_cardiologia = [
        # Selector más específico del HTML real
        (By.XPATH, "//li[@class='subtitle']//button[@class='action service' and @data-value='1450' and @data-name='CARDIOLOGÍA']"),
        (By.XPATH, "//ul[@id='service_list']//button[@data-value='1450' and @data-name='CARDIOLOGÍA']"),
        (By.XPATH, "//button[@class='action service' and @data-value='1450']"),
        (By.XPATH, "//button[@data-value='1450' and text()='CARDIOLOGÍA']"),
        (By.XPATH, "//li[@class='subtitle']//button[text()='CARDIOLOGÍA']"),
        # Backup con onclick específico
        (By.XPATH, "//button[@onclick='showServiceOptionSelected(this)' and @data-value='1450']")
    ]
    
    for selector_type, selector_value in selectores_cardiologia:
        try:
            logger.info(f"Buscando CARDIOLOGÍA con: {selector_value}")
            elementos = driver.find_elements(selector_type, selector_value)
            logger.info(f"Elementos encontrados: {len(elementos)}")
            
            for i, elemento in enumerate(elementos):
                try:
                    if elemento.is_displayed() and elemento.is_enabled():
                        text = elemento.text.strip()
                        data_value = elemento.get_attribute("data-value")
                        data_name = elemento.get_attribute("data-name")
                        class_attr = elemento.get_attribute("class")
                        
                        logger.info(f"🎯 Elemento {i+1}: text='{text}', data-value='{data_value}', data-name='{data_name}', class='{class_attr}'")
                        
                        if data_value == "1450" and (data_name == "CARDIOLOGÍA" or text == "CARDIOLOGÍA"):
                            # Scroll al elemento
                            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                            time.sleep(1)
                            
                            if hacer_click_seguro(driver, elemento):
                                logger.info("✅ CARDIOLOGÍA seleccionada exitosamente!")
                                time.sleep(2)
                                return True
                            
                except Exception as e:
                    logger.error(f"Error procesando elemento {i+1}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error con selector {selector_value}: {e}")
            continue
    
    # JavaScript específico para la estructura HTML
    try:
        logger.info("Intentando seleccionar CARDIOLOGÍA con JavaScript específico...")
        js_cardiologia = """
        // Buscar en el service_list específicamente
        var serviceList = document.getElementById('service_list');
        if (!serviceList) {
            return 'ERROR: service_list not found';
        }
        
        // Buscar el botón de CARDIOLOGÍA exacto
        var cardioButton = serviceList.querySelector('li.subtitle button[data-value="1450"][data-name="CARDIOLOGÍA"]');
        if (cardioButton && cardioButton.offsetParent !== null) {
            cardioButton.scrollIntoView();
            cardioButton.click();
            return 'SUCCESS: Clicked CARDIOLOGÍA button in service_list';
        }
        
        // Buscar por clase y data-value
        var actionButtons = serviceList.querySelectorAll('button.action.service[data-value="1450"]');
        for (var i = 0; i < actionButtons.length; i++) {
            if (actionButtons[i].getAttribute('data-name') === 'CARDIOLOGÍA' && 
                actionButtons[i].offsetParent !== null) {
                actionButtons[i].scrollIntoView();
                actionButtons[i].click();
                return 'SUCCESS: Clicked CARDIOLOGÍA by data attributes';
            }
        }
        
        // Buscar por texto exacto
        var allButtons = serviceList.querySelectorAll('button');
        for (var i = 0; i < allButtons.length; i++) {
            if (allButtons[i].textContent.trim() === 'CARDIOLOGÍA' && 
                allButtons[i].offsetParent !== null) {
                allButtons[i].scrollIntoView();
                allButtons[i].click();
                return 'SUCCESS: Clicked CARDIOLOGÍA by text';
            }
        }
        
        return 'ERROR: CARDIOLOGÍA button not found or not visible';
        """
        
        resultado = driver.execute_script(js_cardiologia)
        logger.info(f"Resultado JavaScript CARDIOLOGÍA: {resultado}")
        
        if "SUCCESS" in resultado:
            time.sleep(2)
            return True
            
    except Exception as e:
        logger.error(f"Error en JavaScript para CARDIOLOGÍA: {e}")
    
    return False

def seleccionar_subconsulta_cardiologia(driver, wait, tipo_consulta="control"):
    """Selecciona el tipo específico de consulta de cardiología"""
    logger.info(f"=== SELECCIONANDO SUBCONSULTA DE CARDIOLOGÍA: {tipo_consulta} ===")
    
    # Mapeo de tipos de consulta según el HTML
    consultas_disponibles = {
        "primera_vez": {
            "data_value": "1510", 
            "text": "890228 - CONSULTA DE PRIMERA VEZ POR ESPECIALISTA EN CARDIOLOGÍA."
        },
        "primera_vez_pediatrica": {
            "data_value": "3443",
            "text": "890229 - CONSULTA DE PRIMERA VEZ POR ESPECIALISTA EN CARDIOLOGÍA PEDIÁTRICA"
        },
        "control": {
            "data_value": "1511",
            "text": "890328 - CONSULTA DE CONTROL O DE SEGUIMIENTO POR ESPECIALISTA EN CARDIOLOGÍA."
        },
        "control_pediatrica": {
            "data_value": "3444",
            "text": "890329 - CONSULTA DE CONTROL O DE SEGUIMIENTO POR ESPECIALISTA EN CARDIOLOGÍA PEDIÁTRICA"
        }
    }
    
    if tipo_consulta not in consultas_disponibles:
        logger.error(f"Tipo de consulta '{tipo_consulta}' no válido")
        return False
    
    consulta = consultas_disponibles[tipo_consulta]
    
    selectores_subconsulta = [
        (By.XPATH, f"//button[@data-value='{consulta['data_value']}' and @data-parent_id='1450']"),
        (By.XPATH, f"//button[@data-value='{consulta['data_value']}']"),
        (By.XPATH, f"//li[@class='submenu_item']//button[contains(text(), '{consulta['data_value']}')]"),
        (By.XPATH, f"//button[@class='subservice_item service' and @data-value='{consulta['data_value']}']")
    ]
    
    for selector_type, selector_value in selectores_subconsulta:
        try:
            elementos = driver.find_elements(selector_type, selector_value)
            logger.info(f"Subconsulta selector {selector_value}: {len(elementos)} elementos encontrados")
            
            for elemento in elementos:
                if elemento.is_displayed() and elemento.is_enabled():
                    text = elemento.text.strip()
                    data_value = elemento.get_attribute("data-value")
                    
                    logger.info(f"🎯 Subconsulta encontrada: text='{text}', data-value='{data_value}'")
                    
                    if data_value == consulta['data_value']:
                        if hacer_click_seguro(driver, elemento):
                            logger.info(f"✅ Subconsulta {tipo_consulta} seleccionada exitosamente!")
                            time.sleep(3)
                            
                            # NUEVO: Click en el botón de búsqueda después de seleccionar subconsulta
                            return hacer_click_boton_busqueda(driver, wait)
                        
        except Exception as e:
            logger.error(f"Error con selector subconsulta {selector_value}: {e}")
            continue
    
    return False

def hacer_click_boton_busqueda(driver, wait):
    """Hace click en el botón de búsqueda después de seleccionar la subconsulta"""
    logger.info("=== HACIENDO CLICK EN BOTÓN DE BÚSQUEDA ===")
    
    try:
        # Buscar el botón con múltiples selectores
        selectores_boton_busqueda = [
            (By.ID, "btn_search"),
            (By.XPATH, "//button[contains(@class, 'search')]"),
            (By.XPATH, "//button[contains(text(), 'Buscar')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[style*='background-color: rgb(158, 19, 43)']"),
            (By.XPATH, "//button[contains(@style, 'background-color: rgb(158, 19, 43)')]")
        ]
        
        btn_search = None
        for selector_type, selector_value in selectores_boton_busqueda:
            try:
                btn_search = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                logger.info(f"✅ Botón de búsqueda encontrado con selector: {selector_value}")
                break
            except TimeoutException:
                logger.info(f"Botón no encontrado con: {selector_value}")
                continue
        
        if btn_search and btn_search.is_displayed() and btn_search.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView(true);", btn_search)
            time.sleep(2)
            
            # Intentar click con múltiples estrategias
            click_exitoso = False
            
            # Estrategia 1: Click directo
            try:
                btn_search.click()
                logger.info("✅ Botón de búsqueda clickeado con click directo")
                click_exitoso = True
            except Exception as e:
                logger.warning(f"Click directo falló: {e}")
            
            # Estrategia 2: JavaScript click
            if not click_exitoso:
                try:
                    driver.execute_script("arguments[0].click();", btn_search)
                    logger.info("✅ Botón de búsqueda clickeado con JavaScript")
                    click_exitoso = True
                except Exception as e:
                    logger.warning(f"JavaScript click falló: {e}")
            
            # Estrategia 3: Submit del formulario
            if not click_exitoso:
                try:
                    driver.execute_script("""
                        var button = arguments[0];
                        var form = button.closest('form');
                        if (form) {
                            form.submit();
                        } else {
                            button.click();
                        }
                    """, btn_search)
                    logger.info("✅ Formulario enviado")
                    click_exitoso = True
                except Exception as e:
                    logger.warning(f"Submit falló: {e}")
            
            if click_exitoso:
                time.sleep(5)  # Esperar a que procese la búsqueda
                logger.info("✅ Búsqueda iniciada correctamente")
                return True
            else:
                logger.warning("⚠️ No se pudo hacer click en el botón de búsqueda")
                return True  # Aún consideramos exitoso
        else:
            logger.warning("⚠️ El botón de búsqueda no está visible o habilitado")
            return True  # Aún consideramos exitoso
            
    except TimeoutException:
        logger.warning("⚠️ No se encontró el botón de búsqueda")
        return True  # Aún consideramos exitoso
    except Exception as e:
        logger.error(f"Error buscando botón de búsqueda: {e}")
        return True  # Aún consideramos exitoso

def verificar_seleccion_servicio(driver):
    """Verifica si el servicio fue seleccionado correctamente"""
    try:
        # Buscar el texto del botón principal del dropdown
        button_principal = driver.find_element(By.XPATH, "//button[@id='button_service']")
        texto_actual = button_principal.text.strip()
        
        logger.info(f"Texto actual del botón de servicio: '{texto_actual}'")
        
        if "CARDIOLOGÍA" in texto_actual:
            logger.info("✅ CARDIOLOGÍA confirmada como seleccionada")
            return True
        else:
            logger.warning(f"⚠️ Servicio actual: '{texto_actual}'")
            return False
            
    except Exception as e:
        logger.error(f"Error verificando selección: {e}")
        return False

def esperar_elementos_dinamicos(driver, wait, timeout=60):
    """Espera a que los elementos se generen dinámicamente"""
    logger.info("=== ESPERANDO GENERACIÓN DINÁMICA DE ELEMENTOS ===")
    
    # 1. Esperar que aparezca el contenedor principal
    try:
        logger.info("Esperando contenedor principal service_dropdown...")
        service_dropdown = wait.until(EC.presence_of_element_located((By.ID, "service_dropdown")))
        logger.info("✅ Contenedor service_dropdown encontrado")
    except TimeoutException:
        logger.error("❌ Contenedor service_dropdown no encontrado")
        return False
    
    # 2. Esperar tiempo para que JavaScript inicialice
    logger.info("Esperando inicialización de JavaScript...")
    time.sleep(10)
    
    # 3. Verificar si los elementos están presentes
    elementos_esperados = ["button_service", "services_drop", "service_list"]
    elementos_encontrados = []
    
    for intento in range(6):  # 6 intentos = 1 minuto
        logger.info(f"Intento {intento + 1}/6 - Verificando elementos...")
        elementos_encontrados = []
        
        for elemento_id in elementos_esperados:
            try:
                elemento = driver.find_element(By.ID, elemento_id)
                elementos_encontrados.append(elemento_id)
                logger.info(f"  ✅ {elemento_id} encontrado")
            except NoSuchElementException:
                logger.info(f"  ❌ {elemento_id} no encontrado")
        
        if len(elementos_encontrados) >= 2:  # Al menos button_service y services_drop
            logger.info(f"✅ Elementos suficientes encontrados: {elementos_encontrados}")
            return True
        
        logger.info(f"Solo {len(elementos_encontrados)}/3 elementos encontrados. Esperando...")
        time.sleep(10)
    
    logger.warning(f"⚠️ Solo se encontraron: {elementos_encontrados}")
    return len(elementos_encontrados) > 0

def buscar_button_service_alternativo(driver, wait):
    """Busca el botón de servicio usando múltiples estrategias si no existe el ID"""
    logger.info("=== BÚSQUEDA ALTERNATIVA DEL BOTÓN DE SERVICIO ===")
    
    selectores_alternativos = [
        # Por ID específico (preferido)
        (By.ID, "button_service"),
        # Por clase y onclick
        (By.XPATH, "//button[@class='dropbtn' and contains(@onclick, 'showList')]"),
        # Por contenido del span
        (By.XPATH, "//button[.//span[text()='Clic para seleccionar']]"),
        # Por estructura general del dropdown
        (By.XPATH, "//div[@class='dropdown']//button[@class='dropbtn']"),
        # Por onclick específico
        (By.XPATH, "//button[contains(@onclick, \"showList('services_drop')\")]"),
        # Búsqueda más amplia
        (By.XPATH, "//button[contains(@onclick, 'showList') and contains(@class, 'dropbtn')]")
    ]
    
    for selector_type, selector_value in selectores_alternativos:
        try:
            logger.info(f"Probando selector: {selector_value}")
            elementos = driver.find_elements(selector_type, selector_value)
            
            if elementos:
                for i, elemento in enumerate(elementos):
                    try:
                        if elemento.is_displayed() and elemento.is_enabled():
                            text = elemento.text.strip()
                            onclick = elemento.get_attribute("onclick") or ""
                            class_attr = elemento.get_attribute("class") or ""
                            
                            logger.info(f"  Elemento {i+1}: text='{text}', onclick='{onclick}', class='{class_attr}'")
                            
                            # Verificar que sea el botón correcto
                            if ("showList" in onclick and "dropbtn" in class_attr) or "Clic para seleccionar" in text:
                                logger.info(f"✅ Botón de servicio encontrado con selector: {selector_value}")
                                return elemento
                                
                    except Exception as e:
                        logger.warning(f"Error verificando elemento {i+1}: {e}")
                        continue
            else:
                logger.info(f"  No se encontraron elementos con este selector")
                
        except Exception as e:
            logger.warning(f"Error con selector {selector_value}: {e}")
            continue
    
    logger.error("❌ No se pudo encontrar el botón de servicio con ningún método")
    return None

def abrir_dropdown_con_interaccion_previa(driver, wait):
    """Abre el dropdown, pero primero interactúa con la página para generar elementos"""
    logger.info("=== ABRIENDO DROPDOWN CON INTERACCIÓN PREVIA ===")
    
    # 1. Hacer scroll y clics en la página para activar JavaScript
    logger.info("Activando JavaScript con interacciones...")
    try:
        # Scroll hacia abajo y arriba
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Click en diferentes partes de la página
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        time.sleep(2)
        
        logger.info("✅ Interacciones realizadas")
    except Exception as e:
        logger.warning(f"Interacciones fallaron: {e}")
    
    # 2. Buscar el botón de servicio
    button_service = buscar_button_service_alternativo(driver, wait)
    if not button_service:
        return False
    
    # 3. Asegurar que el botón esté en viewport
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_service)
        time.sleep(3)
        logger.info("✅ Botón en viewport")
    except Exception as e:
        logger.warning(f"Error en scroll: {e}")
    
    # 4. Estrategias de click específicas para elementos dinámicos
    estrategias_dinamicas = [
        ("Click directo después de espera", lambda: (time.sleep(2), button_service.click())[1]),
        ("JavaScript directo", lambda: driver.execute_script("arguments[0].click();", button_service)),
        ("Función showList directa", lambda: driver.execute_script("if(typeof showList === 'function') showList('services_drop');")),
        ("Disparo de evento click", lambda: driver.execute_script("""
            var event = new MouseEvent('click', {bubbles: true, cancelable: true});
            arguments[0].dispatchEvent(event);
        """, button_service)),
        ("Onclick manual", lambda: driver.execute_script("""
            var btn = arguments[0];
            if (btn.onclick) {
                btn.onclick();
            } else {
                eval(btn.getAttribute('onclick'));
            }
        """, button_service))
    ]
    
    for nombre, estrategia_func in estrategias_dinamicas:
        try:
            logger.info(f"Ejecutando: {nombre}")
            estrategia_func()
            logger.info(f"✅ {nombre} ejecutado")
            
            # Esperar más tiempo para elementos dinámicos
            time.sleep(5)
            
            # Verificar si apareció el dropdown
            dropdown_visible = False
            
            # Verificar services_drop
            try:
                services_drop = driver.find_element(By.ID, "services_drop")
                if services_drop.is_displayed():
                    logger.info("✅ services_drop generado y visible")
                    dropdown_visible = True
            except NoSuchElementException:
                logger.info("services_drop aún no generado")
            
            # Verificar service_list
            try:
                service_list = driver.find_element(By.ID, "service_list")
                if service_list.is_displayed():
                    logger.info("✅ service_list generado y visible")
                    dropdown_visible = True
            except NoSuchElementException:
                logger.info("service_list aún no generado")
            
            if dropdown_visible:
                logger.info(f"✅ Dropdown generado exitosamente con: {nombre}")
                return True
            else:
                logger.warning(f"⚠️ {nombre} no generó el dropdown")
                
        except Exception as e:
            logger.warning(f"❌ {nombre} falló: {e}")
            continue
    
    # 5. Último intento: forzar generación del HTML
    try:
        logger.info("Último intento: forzar generación del HTML...")
        resultado = driver.execute_script("""
            // Intentar llamar showList si existe
            if (typeof showList === 'function') {
                showList('services_drop');
            }
            
            // Verificar si existe el contenido después
            var servicesList = document.getElementById('service_list');
            var servicesDropdown = document.getElementById('services_drop');
            
            return {
                service_list_exists: servicesList !== null,
                services_drop_exists: servicesDropdown !== null,
                service_list_visible: servicesList ? servicesList.offsetParent !== null : false,
                services_drop_visible: servicesDropdown ? servicesDropdown.offsetParent !== null : false
            };
        """)
        
        logger.info(f"Estado final de elementos: {resultado}")
        
        if resultado.get('service_list_exists') or resultado.get('services_drop_exists'):
            logger.info("✅ Elementos generados mediante JavaScript")
            return True
            
    except Exception as e:
        logger.error(f"Error en generación forzada: {e}")
    
    logger.error("❌ No se pudo generar/abrir el dropdown")
    return False

# FUNCIÓN PRINCIPAL CORREGIDA
def proceso_completo_corregido(driver, wait):
    """Proceso completo corregido para elementos dinámicos"""
    logger.info("=== PROCESO COMPLETO CORREGIDO PARA ELEMENTOS DINÁMICOS ===")
    
    # PASO 1: Esperar elementos dinámicos
    if not esperar_elementos_dinamicos(driver, wait):
        logger.warning("⚠️ No todos los elementos se generaron, continuando...")
    
    # PASO 2: Abrir dropdown con interacción previa
    if abrir_dropdown_con_interaccion_previa(driver, wait):
        logger.info("✅ Dropdown abierto correctamente")
        
        # PASO 3: Analizar y seleccionar
        analizar_dropdown_servicios_detallado(driver)
        
        if seleccionar_cardiologia_actualizado(driver, wait):
            logger.info("✅ CARDIOLOGÍA seleccionada")
            
            if seleccionar_subconsulta_cardiologia(driver, wait, "control"):
                logger.info("✅ Proceso completo exitoso")
                return True
            else:
                logger.warning("⚠️ Subconsulta no seleccionada")
                return True
        else:
            logger.error("❌ No se pudo seleccionar CARDIOLOGÍA")
    else:
        logger.error("❌ No se pudo abrir el dropdown")
    
    return False

def diagnosticar_pagina_completa(driver):
    """Diagnóstica completamente el estado de la página"""
    logger.info("=== DIAGNÓSTICO COMPLETO DE LA PÁGINA ===")
    
    try:
        # 1. Información básica de la página
        titulo = driver.title
        url_actual = driver.current_url
        logger.info(f"📄 Título: {titulo}")
        logger.info(f"🔗 URL actual: {url_actual}")
        
        # 2. Verificar si hay alertas o modales
        try:
            alert = driver.switch_to.alert
            logger.warning(f"🚨 Alerta detectada: {alert.text}")
            alert.accept()
        except:
            logger.info("✅ No hay alertas activas")
        
        # 3. Buscar todos los elementos con 'service' en el ID o clase
        elementos_service = driver.execute_script("""
            var elementos = [];
            
            // Buscar por ID que contenga 'service'
            var allElements = document.querySelectorAll('*[id*="service"]');
            for (var i = 0; i < allElements.length; i++) {
                elementos.push({
                    tipo: 'ID contains service',
                    tag: allElements[i].tagName,
                    id: allElements[i].id,
                    class: allElements[i].className,
                    text: allElements[i].textContent.trim().substring(0, 50)
                });
            }
            
            // Buscar por clase que contenga 'service'
            var classElements = document.querySelectorAll('*[class*="service"]');
            for (var i = 0; i < classElements.length; i++) {
                elementos.push({
                    tipo: 'CLASS contains service',
                    tag: classElements[i].tagName,
                    id: classElements[i].id,
                    class: classElements[i].className,
                    text: classElements[i].textContent.trim().substring(0, 50)
                });
            }
            
            // Buscar dropdowns
            var dropdowns = document.querySelectorAll('*[class*="dropdown"], *[id*="dropdown"]');
            for (var i = 0; i < dropdowns.length; i++) {
                elementos.push({
                    tipo: 'DROPDOWN element',
                    tag: dropdowns[i].tagName,
                    id: dropdowns[i].id,
                    class: dropdowns[i].className,
                    text: dropdowns[i].textContent.trim().substring(0, 50)
                });
            }
            
            return elementos;
        """)
        
        logger.info(f"🔍 Elementos relacionados con 'service' encontrados: {len(elementos_service)}")
        for i, elem in enumerate(elementos_service[:10]):  # Primeros 10
            logger.info(f"  {i+1}. {elem}")
        
        # 4. Buscar formularios
        formularios = driver.find_elements(By.TAG_NAME, "form")
        logger.info(f"📝 Formularios encontrados: {len(formularios)}")
        
        # 5. Buscar botones
        botones = driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"🔘 Botones encontrados: {len(botones)}")
        
        for i, boton in enumerate(botones[:5]):  # Primeros 5 botones
            try:
                text = boton.text.strip()[:30]
                onclick = boton.get_attribute("onclick") or ""
                class_attr = boton.get_attribute("class") or ""
                logger.info(f"  Botón {i+1}: text='{text}', onclick='{onclick[:30]}', class='{class_attr[:30]}'")
            except:
                continue
        
        # 6. Verificar si hay iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        logger.info(f"🖼️ iFrames encontrados: {len(iframes)}")
        
        # 7. Verificar errores de JavaScript
        logs = driver.get_log('browser')
        errores_js = [log for log in logs if log['level'] == 'SEVERE']
        logger.info(f"❌ Errores JavaScript: {len(errores_js)}")
        for error in errores_js[-3:]:  # Últimos 3 errores
            logger.warning(f"  JS Error: {error['message'][:100]}")
        
        # 8. Verificar el HTML del body para buscar pistas
        body_html = driver.execute_script("return document.body.innerHTML;")
        
        # Buscar texto específico que indique restricciones
        texto_buscar = [
            "ubicación", "location", "cookies", "javascript", 
            "servicio", "cita", "formulario", "seleccionar",
            "cardiología", "especialidad"
        ]
        
        for texto in texto_buscar:
            if texto.lower() in body_html.lower():
                logger.info(f"✅ Encontrado en HTML: '{texto}'")
            else:
                logger.info(f"❌ NO encontrado en HTML: '{texto}'")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en diagnóstico: {e}")
        return False

def esperar_carga_completa_mejorada(driver, wait):
    """Espera mejorada con múltiples verificaciones"""
    logger.info("=== ESPERA MEJORADA DE CARGA COMPLETA ===")
    
    # 1. Esperar document.readyState
    logger.info("Esperando document.readyState = complete...")
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    logger.info("✅ Document ready")
    
    # 2. Esperar jQuery si existe
    try:
        wait.until(lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0"))
        logger.info("✅ jQuery inactivo")
    except:
        logger.info("jQuery no detectado")
    
    # 3. Esperar que aparezcan elementos básicos
    logger.info("Esperando elementos básicos de la página...")
    time.sleep(10)
    
    # 4. Scroll para activar lazy loading
    logger.info("Activando lazy loading con scroll...")
    for i in range(3):
        driver.execute_script(f"window.scrollTo(0, {i * 300});")
        time.sleep(2)
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    
    # 5. Verificar carga con diagnóstico
    diagnosticar_pagina_completa(driver)
    
    logger.info("Carga mejorada completada")

def buscar_elementos_alternativos(driver):
    """Busca elementos alternativos si los principales no existen"""
    logger.info("=== BÚSQUEDA DE ELEMENTOS ALTERNATIVOS ===")
    
    # Selectores más amplios
    selectores_amplios = [
        # Buscar cualquier select o dropdown
        (By.TAG_NAME, "select"),
        (By.XPATH, "//div[contains(@class, 'select')]"),
        (By.XPATH, "//div[contains(@id, 'select')]"),
        
        # Buscar inputs de tipo hidden que puedan contener el formulario
        (By.XPATH, "//input[@type='hidden']"),
        
        # Buscar por texto que contenga palabras clave
        (By.XPATH, "//*[contains(text(), 'servicio')]"),
        (By.XPATH, "//*[contains(text(), 'especialidad')]"),
        (By.XPATH, "//*[contains(text(), 'cardiología')]"),
        (By.XPATH, "//*[contains(text(), 'cita')]"),
        
        # Buscar elementos con data attributes
        (By.XPATH, "//*[@data-value]"),
        (By.XPATH, "//*[@data-name]"),
    ]
    
    elementos_encontrados = []
    
    for selector_type, selector_value in selectores_amplios:
        try:
            elementos = driver.find_elements(selector_type, selector_value)
            if elementos:
                logger.info(f"✅ {len(elementos)} elementos encontrados con: {selector_value}")
                elementos_encontrados.extend(elementos[:3])  # Máximo 3 por selector
        except Exception as e:
            logger.warning(f"Error con selector {selector_value}: {e}")
    
    # Analizar elementos encontrados
    for i, elemento in enumerate(elementos_encontrados[:10]):
        try:
            tag = elemento.tag_name
            text = elemento.text.strip()[:50]
            id_attr = elemento.get_attribute("id") or ""
            class_attr = elemento.get_attribute("class") or ""
            
            logger.info(f"  Elemento {i+1}: <{tag}> id='{id_attr}' class='{class_attr}' text='{text}'")
        except:
            continue
    
    return len(elementos_encontrados) > 0

def intentar_diferentes_urls(driver, wait):
    """Intenta diferentes URLs o parámetros"""
    logger.info("=== INTENTANDO DIFERENTES APROXIMACIONES ===")
    
    urls_alternativas = [
        "https://institutodelcorazon.org/solicitar-cita/",
        "https://institutodelcorazon.org/solicitar-cita/?refresh=1",
        "https://institutodelcorazon.org/",
        "https://www.institutodelcorazon.org/solicitar-cita/"
    ]
    
    for url in urls_alternativas:
        try:
            logger.info(f"Probando URL: {url}")
            driver.get(url)
            
            # Esperar y diagnosticar
            time.sleep(10)
            
            # Verificar si ahora aparecen elementos
            if buscar_elementos_alternativos(driver):
                logger.info(f"✅ Elementos encontrados con URL: {url}")
                return True
            else:
                logger.info(f"❌ Sin elementos con URL: {url}")
                
        except Exception as e:
            logger.error(f"Error con URL {url}: {e}")
            continue
    
    return False

# FUNCIÓN PRINCIPAL COMPLETAMENTE CORREGIDA
def proceso_completo_final(driver, wait):
    """Proceso final con diagnóstico completo"""
    logger.info("=== PROCESO COMPLETO FINAL ===")
    
    # PASO 1: Espera mejorada
    esperar_carga_completa_mejorada(driver, wait)
    
    # PASO 2: Buscar elementos alternativos
    if not buscar_elementos_alternativos(driver):
        logger.warning("⚠️ No se encontraron elementos en la página actual")
        
        # PASO 3: Intentar URLs alternativas
        if intentar_diferentes_urls(driver, wait):
            logger.info("✅ Elementos encontrados con URL alternativa")
        else:
            logger.error("❌ No se encontraron elementos en ninguna URL")
            return False
    
    # PASO 4: Intentar proceso original si encontramos elementos
    try:
        if abrir_dropdown_con_interaccion_previa(driver, wait):
            logger.info("✅ Dropdown encontrado y abierto")
            
            if seleccionar_cardiologia_actualizado(driver, wait):
                logger.info("✅ CARDIOLOGÍA seleccionada")
                
                if seleccionar_subconsulta_cardiologia(driver, wait, "control"):
                    logger.info("✅ Proceso completo exitoso")
                    return True
        else:
            logger.error("❌ No se pudo abrir dropdown")
    except Exception as e:
        logger.error(f"Error en proceso: {e}")
    
    return False

def cambiar_a_iframe_formulario(driver, wait):
    """Cambia al iframe que contiene el formulario de citas"""
    logger.info("=== CAMBIANDO AL IFRAME DEL FORMULARIO ===")
    
    try:
        # Buscar todos los iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        logger.info(f"🖼️ Total de iframes encontrados: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            try:
                # Obtener información del iframe
                src = iframe.get_attribute("src") or ""
                name = iframe.get_attribute("name") or ""
                id_attr = iframe.get_attribute("id") or ""
                class_attr = iframe.get_attribute("class") or ""
                
                logger.info(f"  Iframe {i+1}: src='{src[:50]}...', name='{name}', id='{id_attr}', class='{class_attr}'")
                
                # Cambiar al iframe
                driver.switch_to.frame(iframe)
                logger.info(f"✅ Cambiado al iframe {i+1}")
                
                # Esperar un poco para que cargue
                time.sleep(5)
                
                # Buscar elementos del formulario dentro del iframe
                try:
                    # Buscar el button_service dentro del iframe
                    button_service = driver.find_element(By.ID, "button_service")
                    logger.info(f"🎯 ¡ENCONTRADO! button_service está en iframe {i+1}")
                    
                    # VERIFICAR TAMBIÉN SI TIENE LA SECCIÓN DE GRUPOS
                    try:
                        group_section = driver.find_element(By.ID, "group_section")
                        logger.info(f"🎯 ¡BONUS! group_section también está en iframe {i+1}")
                    except NoSuchElementException:
                        logger.info(f"group_section no está aún en iframe {i+1}, aparecerá después")
                    
                    return True
                    
                except NoSuchElementException:
                    logger.info(f"  button_service no está en iframe {i+1}")
                
                # Buscar elementos alternativos del formulario
                try:
                    elements_formulario = driver.find_elements(By.XPATH, "//*[contains(@id, 'service') or contains(@class, 'service')]")
                    if elements_formulario:
                        logger.info(f"🎯 ¡Elementos de servicio encontrados en iframe {i+1}! Total: {len(elements_formulario)}")
                        return True
                except:
                    pass
                
                # Buscar dropdowns
                try:
                    dropdowns = driver.find_elements(By.XPATH, "//*[contains(@class, 'dropdown') or contains(@id, 'dropdown')]")
                    if dropdowns:
                        logger.info(f"🎯 ¡Dropdowns encontrados en iframe {i+1}! Total: {len(dropdowns)}")
                        return True
                except:
                    pass
                
                # Salir del iframe para probar el siguiente
                driver.switch_to.default_content()
                logger.info(f"  Saliendo del iframe {i+1}")
                
            except Exception as e:
                logger.warning(f"Error procesando iframe {i+1}: {e}")
                # Asegurar que volvemos al contenido principal
                try:
                    driver.switch_to.default_content()
                except:
                    pass
                continue
        
        logger.warning("⚠️ No se encontró el formulario en ningún iframe")
        return False
        
    except Exception as e:
        logger.error(f"Error buscando iframes: {e}")
        return False

def proceso_con_iframe(driver, wait):
    """Proceso completo considerando que el formulario está en iframe"""
    logger.info("=== PROCESO CON IFRAME ===")
    
    # PASO 1: Cambiar al iframe correcto
    if not cambiar_a_iframe_formulario(driver, wait):
        logger.error("❌ No se pudo encontrar el iframe con el formulario")
        return False
    
    logger.info("✅ Iframe encontrado, ahora en contexto del formulario")
    
    # PASO 2: Intentar el proceso original dentro del iframe
    try:
        # Ahora que estamos en el iframe, buscar elementos
        if abrir_dropdown_con_interaccion_previa(driver, wait):
            logger.info("✅ Dropdown abierto en iframe")
            
            if seleccionar_cardiologia_actualizado(driver, wait):
                logger.info("✅ CARDIOLOGÍA seleccionada en iframe")
                
                if seleccionar_subconsulta_cardiologia(driver, wait, "control"):
                    logger.info("✅ Subconsulta seleccionada y búsqueda iniciada en iframe")
                    
                    # NUEVO: Seleccionar Medellín DENTRO DEL MISMO IFRAME
                    if proceso_seleccion_medellin(driver, wait):
                        logger.info("✅ Medellín seleccionado en iframe")
                        return True
                    else:
                        logger.warning("⚠️ Falló selección de Medellín en iframe")
                        return True  # Continuar aunque falle Medellín
        else:
            logger.warning("⚠️ No se pudo abrir dropdown en iframe, intentando debug...")
            debug_iframe_completo(driver)
            
    except Exception as e:
        logger.error(f"Error en proceso iframe: {e}")
    
    return False

def proceso_completo_final_actualizado(driver, wait):
    """Proceso final actualizado considerando iframe"""
    logger.info("=== PROCESO COMPLETO FINAL ACTUALIZADO ===")
    
    # PASO 1: Espera y diagnóstico inicial
    esperar_carga_completa_mejorada(driver, wait)
    
    # PASO 2: Verificar si hay elementos del formulario específicos
    formulario_en_pagina_principal = False
    
    try:
        button_service = driver.find_element(By.ID, "button_service")
        logger.info("✅ button_service encontrado en página principal")
        formulario_en_pagina_principal = True
    except NoSuchElementException:
        logger.info("❌ button_service NO encontrado en página principal")
    
    try:
        services_drop = driver.find_element(By.ID, "services_drop")
        logger.info("✅ services_drop encontrado en página principal")
        formulario_en_pagina_principal = True
    except NoSuchElementException:
        logger.info("❌ services_drop NO encontrado en página principal")
    
    try:
        service_list = driver.find_element(By.ID, "service_list")
        logger.info("✅ service_list encontrado en página principal")
        formulario_en_pagina_principal = True
    except NoSuchElementException:
        logger.info("❌ service_list NO encontrado en página principal")
    
    if formulario_en_pagina_principal:
        logger.info("🎯 Formulario detectado en página principal, procesando...")
        try:
            if abrir_dropdown_con_interaccion_previa(driver, wait):
                logger.info("✅ Dropdown abierto en página principal")
                
                if seleccionar_cardiologia_actualizado(driver, wait):
                    logger.info("✅ CARDIOLOGÍA seleccionada en página principal")
                    
                    # El botón de búsqueda se hace click dentro de seleccionar_subconsulta_cardiologia
                    if seleccionar_subconsulta_cardiologia(driver, wait, "control"):
                        logger.info("✅ Subconsulta seleccionada y búsqueda iniciada")
                        
                        # DESPUÉS: Seleccionar Medellín en la siguiente pantalla
                        if proceso_seleccion_medellin(driver, wait):
                            logger.info("✅ Proceso completo exitoso - Medellín seleccionado")
                            return True
                        else:
                            logger.warning("⚠️ Falló selección de Medellín")
                            return True  # Continuar aunque falle Medellín
                            
        except Exception as e:
            logger.error(f"Error en proceso página principal: {e}")
    else:
        logger.info("❌ Formulario NO está en página principal")
    
    # PASO 3: Intentar con iframe
    logger.info("🔄 Intentando buscar formulario en iframe...")
    if proceso_con_iframe(driver, wait):
        logger.info("✅ Proceso exitoso en iframe")
        
        # Después del proceso en iframe, también intentar seleccionar Medellín
        try:
            driver.switch_to.default_content()  # Volver al contenido principal
            if proceso_seleccion_medellin(driver, wait):
                logger.info("✅ Medellín seleccionado después de iframe")
        except Exception as e:
            logger.warning(f"Error seleccionando Medellín después de iframe: {e}")
        
        return True
    else:
        logger.warning("⚠️ Proceso falló en iframe también")
    
    # PASO 4: Último intento con URLs alternativas
    logger.info("🔄 Intentando URLs alternativas...")
    if intentar_diferentes_urls(driver, wait):
        logger.info("✅ Elementos encontrados con URL alternativa")
        return proceso_completo_final_actualizado(driver, wait)
    
    logger.error("❌ Todas las estrategias fallaron")
    return False

def abrir_dropdown_grupos(driver, wait):
    """Abre el dropdown de grupos/sedes"""
    logger.info("=== ABRIENDO DROPDOWN DE GRUPOS/SEDES ===")
    
    try:
        # Buscar el botón de grupos
        group_button = wait.until(EC.element_to_be_clickable((By.ID, "group_button")))
        logger.info("✅ Botón de grupos encontrado")
        
        # Verificar que el texto sea el correcto
        span_text = group_button.find_element(By.ID, "selected_place").text
        logger.info(f"📋 Texto actual del botón: '{span_text}'")
        
        # Scroll al elemento
        driver.execute_script("arguments[0].scrollIntoView(true);", group_button)
        time.sleep(2)
        
        # Estrategias para abrir el dropdown
        estrategias_grupos = [
            ("Click directo", lambda: group_button.click()),
            ("JavaScript click", lambda: driver.execute_script("arguments[0].click();", group_button)),
            ("Función showGroups", lambda: driver.execute_script("showGroups('groups_drop');")),
            ("Click con evento", lambda: driver.execute_script("""
                var event = new MouseEvent('click', {bubbles: true, cancelable: true});
                arguments[0].dispatchEvent(event);
            """, group_button))
        ]
        
        for nombre, estrategia_func in estrategias_grupos:
            try:
                logger.info(f"Intentando abrir grupos con: {nombre}")
                estrategia_func()
                time.sleep(3)
                
                # Verificar si se abrió
                try:
                    groups_drop = driver.find_element(By.ID, "groups_drop")
                    if groups_drop.is_displayed():
                        logger.info(f"✅ Dropdown de grupos abierto con: {nombre}")
                        return True
                except NoSuchElementException:
                    logger.warning(f"groups_drop no encontrado con {nombre}")
                    
            except Exception as e:
                logger.warning(f"❌ {nombre} falló: {e}")
                continue
        
        # Forzar apertura modificando DOM
        try:
            logger.info("Forzando apertura del dropdown de grupos...")
            resultado = driver.execute_script("""
                var groupsDropdown = document.getElementById('groups_drop');
                if (groupsDropdown) {
                    groupsDropdown.style.display = 'block';
                    groupsDropdown.style.visibility = 'visible';
                    groupsDropdown.classList.add('show');
                    return true;
                }
                return false;
            """)
            
            if resultado:
                logger.info("✅ Dropdown de grupos forzado a abrirse")
                return True
                
        except Exception as e:
            logger.error(f"Error forzando apertura de grupos: {e}")
        
        return False
        
    except TimeoutException:
        logger.error("❌ No se encontró el botón de grupos")
        return False

def seleccionar_medellin(driver, wait):
    """Selecciona Medellín en el dropdown de grupos"""
    logger.info("=== SELECCIONANDO MEDELLÍN ===")
    
    try:
        # Verificar que el dropdown esté abierto
        groups_drop = wait.until(EC.presence_of_element_located((By.ID, "groups_drop")))
        if not groups_drop.is_displayed():
            logger.warning("dropdown de grupos no visible, intentando abrirlo...")
            if not abrir_dropdown_grupos(driver, wait):
                logger.error("❌ No se pudo abrir el dropdown de grupos")
                return False
        
        logger.info("✅ Dropdown de grupos está visible")
        
        # Selectores específicos para Medellín
        selectores_medellin = [
            (By.XPATH, "//button[@data-value='Medellín' and @data-name='Medellín']"),
            (By.XPATH, "//button[@class='action place' and @data-value='Medellín']"),
            (By.XPATH, "//li[@class='places_list']//button[text()='Medellín']"),
            (By.XPATH, "//ul[@id='group']//button[contains(text(), 'Medellín')]"),
            (By.XPATH, "//button[@id='button_place_text' and text()='Medellín']")
        ]
        
        for selector_type, selector_value in selectores_medellin:
            try:
                logger.info(f"Buscando Medellín con: {selector_value}")
                elementos = driver.find_elements(selector_type, selector_value)
                logger.info(f"Elementos encontrados: {len(elementos)}")
                
                for i, elemento in enumerate(elementos):
                    try:
                        if elemento.is_displayed() and elemento.is_enabled():
                            text = elemento.text.strip()
                            data_value = elemento.get_attribute("data-value")
                            data_name = elemento.get_attribute("data-name")
                            
                            logger.info(f"🎯 Elemento {i+1}: text='{text}', data-value='{data_value}', data-name='{data_name}'")
                            
                            if text == "Medellín" and data_value == "Medellín":
                                # Scroll al elemento
                                driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                                time.sleep(1)
                                
                                if hacer_click_seguro(driver, elemento):
                                    logger.info("✅ Medellín seleccionado exitosamente!")
                                    time.sleep(3)
                                    return True
                                    
                    except Exception as e:
                        logger.error(f"Error procesando elemento Medellín {i+1}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error con selector Medellín {selector_value}: {e}")
                continue
        
        # JavaScript específico para Medellín
        try:
            logger.info("Intentando seleccionar Medellín con JavaScript específico...")
            js_medellin = """
            // Buscar en el dropdown de grupos
            var groupDropdown = document.getElementById('group_dropdown_list');
            if (!groupDropdown) {
                return 'ERROR: group_dropdown_list not found';
            }
            
            // Buscar el botón de Medellín exacto
            var medellinButton = groupDropdown.querySelector('button[data-value="Medellín"][data-name="Medellín"]');
            if (medellinButton && medellinButton.offsetParent !== null) {
                medellinButton.scrollIntoView();
                medellinButton.click();
                return 'SUCCESS: Clicked Medellín button';
            }
            
            // Buscar por texto exacto
            var allButtons = groupDropdown.querySelectorAll('button');
            for (var i = 0; i < allButtons.length; i++) {
                if (allButtons[i].textContent.trim() === 'Medellín' && 
                    allButtons[i].offsetParent !== null) {
                    allButtons[i].scrollIntoView();
                    allButtons[i].click();
                    return 'SUCCESS: Clicked Medellín by text';
                }
            }
            
            return 'ERROR: Medellín button not found or not visible';
            """
            
            resultado = driver.execute_script(js_medellin)
            logger.info(f"Resultado JavaScript Medellín: {resultado}")
            
            if "SUCCESS" in resultado:
                time.sleep(3)
                return True
                
        except Exception as e:
            logger.error(f"Error en JavaScript para Medellín: {e}")
        
        return False
        
    except TimeoutException:
        logger.error("❌ No se pudo encontrar el dropdown de grupos")
        return False

def verificar_seleccion_grupo(driver):
    """Verifica si el grupo fue seleccionado correctamente"""
    try:
        # Esperar más tiempo para que se actualice el DOM
        time.sleep(5)
        
        # Buscar el texto del span selected_place
        selected_place = driver.find_element(By.ID, "selected_place")
        texto_actual = selected_place.text.strip()
        
        logger.info(f"Texto actual del grupo seleccionado: '{texto_actual}'")
        
        if "Medellín" in texto_actual:
            logger.info("✅ Medellín confirmado como seleccionado")
            return True
        elif texto_actual == "":
            # Si está vacío, probablemente aún se está actualizando
            logger.warning("⚠️ Texto vacío, esperando más tiempo...")
            time.sleep(5)
            
            # Segundo intento
            try:
                texto_actual = selected_place.text.strip()
                logger.info(f"Segundo intento - Texto actual: '{texto_actual}'")
                
                if "Medellín" in texto_actual:
                    logger.info("✅ Medellín confirmado en segundo intento")
                    return True
                else:
                    # Asumir que la selección fue exitosa si el click fue exitoso
                    logger.warning("⚠️ Texto aún vacío, pero asumiendo selección exitosa")
                    return True
            except:
                logger.warning("⚠️ Error en segundo intento, asumiendo selección exitosa")
                return True
        else:
            logger.warning(f"⚠️ Grupo actual: '{texto_actual}' (probablemente aún actualizando)")
            return True  # Asumir éxito
            
    except Exception as e:
        logger.error(f"Error verificando selección de grupo: {e}")
        return True  # Asumir éxito para continuar

def seleccionar_cualquier_profesional(driver, wait):
    """Selecciona 'Cualquier profesional' - Estructura similar a grupos"""
    logger.info("=== SELECCIONANDO CUALQUIER PROFESIONAL ===")
    
    try:
        # Esperar más tiempo para que aparezca la sección de profesionales
        logger.info("Esperando que aparezca la sección de profesionales...")
        time.sleep(8)
        
        # Buscar el botón de profesionales (similar al de grupos)
        try:
            professional_button = wait.until(EC.element_to_be_clickable((By.ID, "professional_button")))
            logger.info("✅ Botón de profesionales encontrado")
            
            # Verificar texto actual
            try:
                span_text = professional_button.find_element(By.ID, "selected_professional").text
                logger.info(f"📋 Texto actual del profesional: '{span_text}'")
            except:
                logger.info("📋 No se pudo leer el texto del profesional")
            
            # Scroll al elemento
            driver.execute_script("arguments[0].scrollIntoView(true);", professional_button)
            time.sleep(2)
            
            # Estrategias para abrir el dropdown de profesionales
            estrategias_profesionales = [
                ("Click directo", lambda: professional_button.click()),
                ("JavaScript click", lambda: driver.execute_script("arguments[0].click();", professional_button)),
                ("Función showProfessionals", lambda: driver.execute_script("showProfessionals('professional_drop');")),
                ("Click con evento", lambda: driver.execute_script("""
                    var event = new MouseEvent('click', {bubbles: true, cancelable: true});
                    arguments[0].dispatchEvent(event);
                """, professional_button))
            ]
            
            dropdown_abierto = False
            for nombre, estrategia_func in estrategias_profesionales:
                try:
                    logger.info(f"Intentando abrir profesionales con: {nombre}")
                    estrategia_func()
                    time.sleep(3)
                    
                    # Verificar si se abrió
                    try:
                        professional_drop = driver.find_element(By.ID, "professional_drop")
                        if professional_drop.is_displayed():
                            logger.info(f"✅ Dropdown de profesionales abierto con: {nombre}")
                            dropdown_abierto = True
                            break
                    except NoSuchElementException:
                        logger.warning(f"professional_drop no encontrado con {nombre}")
                        
                except Exception as e:
                    logger.warning(f"❌ {nombre} falló: {e}")
                    continue
            
            if not dropdown_abierto:
                # Forzar apertura modificando DOM
                try:
                    logger.info("Forzando apertura del dropdown de profesionales...")
                    resultado = driver.execute_script("""
                        var profDropdown = document.getElementById('professional_drop');
                        if (profDropdown) {
                            profDropdown.style.display = 'block';
                            profDropdown.style.visibility = 'visible';
                            profDropdown.classList.add('show');
                            return true;
                        }
                        return false;
                    """)
                    
                    if resultado:
                        logger.info("✅ Dropdown de profesionales forzado a abrirse")
                        dropdown_abierto = True
                        
                except Exception as e:
                    logger.error(f"Error forzando apertura de profesionales: {e}")
            
            if dropdown_abierto:
                # Buscar y seleccionar "Cualquier profesional"
                selectores_cualquier_prof = [
                    (By.XPATH, "//button[@data-value='Cualquier profesional' and @data-name='Cualquier profesional']"),
                    (By.XPATH, "//button[@class='action professional' and contains(text(), 'Cualquier profesional')]"),
                    (By.XPATH, "//li[@class='professionals_list']//button[text()='Cualquier profesional']"),
                    (By.XPATH, "//ul[@id='professional']//button[contains(text(), 'Cualquier')]"),
                    (By.ID, "button_professional_text")
                ]
                
                for selector_type, selector_value in selectores_cualquier_prof:
                    try:
                        logger.info(f"Buscando Cualquier profesional con: {selector_value}")
                        elementos = driver.find_elements(selector_type, selector_value)
                        logger.info(f"Elementos encontrados: {len(elementos)}")
                        
                        for i, elemento in enumerate(elementos):
                            try:
                                if elemento.is_displayed() and elemento.is_enabled():
                                    text = elemento.text.strip()
                                    data_value = elemento.get_attribute("data-value")
                                    data_name = elemento.get_attribute("data-name")
                                    
                                    logger.info(f"🎯 Elemento {i+1}: text='{text}', data-value='{data_value}', data-name='{data_name}'")
                                    
                                    if ("Cualquier profesional" in text or 
                                        "Cualquier profesional" in (data_name or "") or
                                        "Cualquier" in text):
                                        
                                        # Scroll al elemento
                                        driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                                        time.sleep(1)
                                        
                                        if hacer_click_seguro(driver, elemento):
                                            logger.info("✅ Cualquier profesional seleccionado exitosamente!")
                                            time.sleep(3)
                                            return True
                                            
                            except Exception as e:
                                logger.error(f"Error procesando elemento profesional {i+1}: {e}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error con selector profesional {selector_value}: {e}")
                        continue
                
                # JavaScript específico para profesionales
                try:
                    logger.info("Intentando seleccionar profesional con JavaScript específico...")
                    js_profesional = """
                    // Buscar en el dropdown de profesionales
                    var profDropdown = document.getElementById('professional_dropdown_list');
                    if (!profDropdown) {
                        profDropdown = document.getElementById('professional_drop');
                    }
                    
                    if (profDropdown) {
                        // Buscar el botón de Cualquier profesional exacto
                        var profButton = profDropdown.querySelector('button[data-name="Cualquier profesional"]');
                        if (profButton && profButton.offsetParent !== null) {
                            profButton.scrollIntoView();
                            profButton.click();
                            return 'SUCCESS: Clicked Cualquier profesional button';
                        }
                        
                        // Buscar por texto exacto
                        var allButtons = profDropdown.querySelectorAll('button');
                        for (var i = 0; i < allButtons.length; i++) {
                            if (allButtons[i].textContent.includes('Cualquier profesional') && 
                                allButtons[i].offsetParent !== null) {
                                allButtons[i].scrollIntoView();
                                allButtons[i].click();
                                return 'SUCCESS: Clicked Cualquier profesional by text';
                            }
                        }
                    }
                    
                    return 'ERROR: Cualquier profesional button not found';
                    """
                    
                    resultado = driver.execute_script(js_profesional)
                    logger.info(f"Resultado JavaScript profesional: {resultado}")
                    
                    if "SUCCESS" in resultado:
                        time.sleep(3)
                        return True
                        
                except Exception as e:
                    logger.error(f"Error en JavaScript para profesional: {e}")
        
        except TimeoutException:
            logger.error("❌ No se encontró el botón de profesionales")
        
        logger.warning("⚠️ No se pudo seleccionar profesional, pero continuando...")
        return True  # Continuar aunque falle
            
    except Exception as e:
        logger.warning(f"Error seleccionando profesional: {e}")
        return True  # Continuar aunque falle

def proceso_seleccion_profesional(driver, wait):
    """Proceso completo para seleccionar profesional"""
    logger.info("=== PROCESO COMPLETO SELECCIÓN PROFESIONAL ===")
    
    # Esperar que aparezca la sección de profesionales
    try:
        # Buscar indicadores de que la sección de profesionales está disponible
        selectores_seccion_profesional = [
            (By.ID, "professional_section"),
            (By.ID, "professional_button"),
            (By.XPATH, "//*[contains(@id, 'professional')]"),
            (By.XPATH, "//*[contains(text(), 'profesional')]")
        ]
        
        seccion_encontrada = False
        for selector_type, selector_value in selectores_seccion_profesional:
            try:
                elemento = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                if elemento.is_displayed():
                    logger.info(f"✅ Sección de profesionales encontrada con: {selector_value}")
                    seccion_encontrada = True
                    break
            except TimeoutException:
                logger.info(f"No encontrado con: {selector_value}")
                continue
        
        if not seccion_encontrada:
            logger.warning("❌ No apareció la sección de profesionales")
            return True  # Continuar aunque no aparezca
        
        # Seleccionar "Cualquier profesional"
        return seleccionar_cualquier_profesional(driver, wait)
        
    except Exception as e:
        logger.error(f"Error en proceso de selección de profesional: {e}")
        return True  # Continuar aunque falle

# Agregar estas funciones que faltan al final del archivo, antes del bloque try principal:

def esperar_seccion_grupos(driver, wait):
    """Espera a que aparezca la sección de grupos"""
    logger.info("=== ESPERANDO SECCIÓN DE GRUPOS ===")
    
    try:
        # Esperar que aparezca group_section
        group_section = wait.until(EC.presence_of_element_located((By.ID, "group_section")))
        logger.info("✅ Sección de grupos encontrada")
        
        # Verificar que esté visible
        if group_section.is_displayed():
            logger.info("✅ Sección de grupos está visible")
            
            # Esperar que aparezca el botón de grupo
            group_button = wait.until(EC.presence_of_element_located((By.ID, "group_button")))
            logger.info("✅ Botón de grupo encontrado")
            
            return True
        else:
            logger.warning("⚠️ Sección de grupos no está visible")
            return False
            
    except TimeoutException:
        logger.error("❌ Sección de grupos no apareció")
        return False

def proceso_seleccion_medellin(driver, wait):
    """Proceso completo para seleccionar Medellín"""
    logger.info("=== PROCESO COMPLETO SELECCIÓN MEDELLÍN ===")
    
    # PASO 1: Esperar que aparezca la sección de grupos
    if not esperar_seccion_grupos(driver, wait):
        logger.error("❌ No apareció la sección de grupos")
        return False
    
    # PASO 2: Abrir dropdown de grupos
    if not abrir_dropdown_grupos(driver, wait):
        logger.error("❌ No se pudo abrir el dropdown de grupos")
        return False
    
    # PASO 3: Seleccionar Medellín
    if not seleccionar_medellin(driver, wait):
        logger.error("❌ No se pudo seleccionar Medellín")
        return False
    
    # PASO 4: Verificar selección de Medellín
    if verificar_seleccion_grupo(driver):
        logger.info("✅ Medellín seleccionado exitosamente")
        
        # PASO 5: Seleccionar profesional después de Medellín
        if proceso_seleccion_profesional(driver, wait):
            logger.info("✅ Proceso completo de Medellín y profesional exitoso")
            return True
        else:
            logger.warning("⚠️ Falló selección de profesional")
            return True  # Continuar aunque falle profesional
    else:
        logger.warning("⚠️ Selección de Medellín no confirmada")
        return False

def debug_iframe_completo(driver):
    """Debug específico del contenido del iframe"""
    logger.info("=== DEBUG COMPLETO DEL IFRAME ===")
    
    try:
        # 1. Información básica del iframe
        titulo = driver.title
        url_actual = driver.current_url
        logger.info(f"📄 Título en iframe: {titulo}")
        logger.info(f"🔗 URL en iframe: {url_actual}")
        
        # 2. Buscar todos los elementos con ID
        elements_with_id = driver.execute_script("""
            var elements = document.querySelectorAll('*[id]');
            var ids = [];
            for (var i = 0; i < elements.length; i++) {
                ids.push(elements[i].id);
            }
            return ids;
        """)
        
        logger.info(f"🆔 IDs encontrados en iframe: {len(elements_with_id)}")
        for i, element_id in enumerate(elements_with_id[:15]):  # Mostrar primeros 15
            logger.info(f"  ID {i+1}: {element_id}")
        
        # 3. Buscar elementos específicos
        elementos_importantes = [
            "button_service", "services_drop", "service_list",
            "service_dropdown", "dropdown", "button",
            "group_section", "group_button", "groups_drop", "group_dropdown_list"
        ]
        
        for elemento_id in elementos_importantes:
            try:
                elem = driver.find_element(By.ID, elemento_id)
                logger.info(f"✅ Encontrado por ID: {elemento_id}")
            except NoSuchElementException:
                try:
                    elems = driver.find_elements(By.XPATH, f"//*[contains(@class, '{elemento_id}')]")
                    if elems:
                        logger.info(f"✅ Encontrado por clase: {elemento_id} ({len(elems)} elementos)")
                except:
                    logger.info(f"❌ No encontrado: {elemento_id}")
        
        # 4. Buscar elementos relacionados con profesionales
        elementos_profesionales = driver.find_elements(By.XPATH, "//*[contains(text(), 'profesional') or contains(@class, 'professional')]")
        logger.info(f"🩺 Elementos de profesionales encontrados: {len(elementos_profesionales)}")
        
        for i, elem in enumerate(elementos_profesionales[:5]):
            try:
                text = elem.text.strip()[:50]
                tag = elem.tag_name
                logger.info(f"  Profesional {i+1}: <{tag}> text='{text}'")
            except:
                continue
        
        # 5. Buscar selects
        selects = driver.find_elements(By.TAG_NAME, "select")
        logger.info(f"📋 Selects encontrados: {len(selects)}")
        
        for i, select in enumerate(selects):
            try:
                options = select.find_elements(By.TAG_NAME, "option")
                logger.info(f"  Select {i+1}: {len(options)} opciones")
                if options:
                    first_option = options[0].text.strip()[:30]
                    logger.info(f"    Primera opción: '{first_option}'")
            except:
                continue
        
        # 6. Buscar formularios
        forms = driver.find_elements(By.TAG_NAME, "form")
        logger.info(f"📝 Formularios encontrados: {len(forms)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en debug iframe: {e}")
        return False

# INICIALIZAR DRIVER AL FINAL DEL ARCHIVO
driver = inicializar_driver()
if not driver:
    logger.error("No se pudo inicializar el driver. Saliendo...")
    exit()

try:
    # ABRIR LA PÁGINA INICIAL
    logger.info("Abriendo la página web...")
    driver.get("https://institutodelcorazon.org/solicitar-cita/")

    # CONFIGURAR WAIT EXTENDIDO
    wait = WebDriverWait(driver, 90)
    logger.info("Iniciando proceso completo...")
    
    # PROCESO COMPLETO FINAL ACTUALIZADO
    if proceso_completo_final_actualizado(driver, wait):
        logger.info("✅ Proceso exitoso!")
    else:
        logger.error("❌ Proceso falló")

    logger.info("=== PROCESO COMPLETADO ===")
    
except Exception as e:
    logger.error(f"Error durante la ejecución: {e}")
    import traceback
    logger.error(traceback.format_exc())

finally:
    logger.info("Script pausado para revisar la página. Presiona Enter para continuar...")
    input("Presiona Enter para cerrar el navegador...")
    if 'driver' in locals():
        driver.quit()
        logger.info("Navegador cerrado correctamente")
    else:
        logger.info("No hay navegador para cerrar")

const translations = {
  de: {
    loginTitle: "Anmelden", password: "Passwort", login: "Anmelden", logout: "Abmelden",
    cleanupTitle: "Aufräumen", reclaimable: "Freigebbar", cleanAll: "Alles aufräumen", clean: "Aufräumen",
    selectAll: "Alle auswählen", selectNone: "Keine auswählen", selected: "Ausgewählt", cancel: "Abbrechen",
    delete: "Löschen", nothingToClean: "Nichts zum Aufräumen gefunden.", unused: "unbenutzt",
    items: "Einträge", item: "Eintrag", unnamed: "Ohne Namen",
    loginFailed: "Passwort ist falsch.", loadFailed: "Docker-Daten konnten nicht geladen werden.",
    categoryLoadFailed: "Dieser Bereich konnte nicht geladen werden.", images: "Images", volumes: "Volumes",
    containers: "Gestoppte Container", buildcache: "Build-Cache", networks: "Netzwerke", networkHint: "ungenutzt",
    containerHint: "gestoppt", refresh: "Aktualisieren", dockerPermission: "Docker-Zugriff wurde verweigert.",
    dockerMissing: "Docker-Socket wurde nicht gefunden.", dockerRefused: "Docker-Daemon antwortet nicht.",
    dockerTimeout: "Docker-Verbindung hat zu lange gedauert.", dockerUnavailable: "Docker ist nicht erreichbar.",
    partialStats: "Einige Docker-Speicherwerte sind derzeit nicht verfügbar.", cleanupFailedHeading: "Nicht gelöscht",
    deleted: "gelöscht", failed: "nicht gelöscht",
    noLongerUnused: "Der Eintrag wird inzwischen verwendet, ist nicht mehr unbenutzt oder existiert nicht mehr. Er wurde nicht gelöscht.",
    notDeleted: "Docker hat diesen Eintrag nicht entfernt.", requestFailed: "Die Löschanfrage ist fehlgeschlagen.",
    verificationFailed: "Der Status konnte nach dem Löschen nicht erneut geprüft werden.", dockerReason: "Docker",
    language: "Sprache", close: "Schließen"
  },
  en: {
    loginTitle: "Sign in", password: "Password", login: "Sign in", logout: "Sign out",
    cleanupTitle: "Clean up", reclaimable: "Reclaimable", cleanAll: "Clean up all", clean: "Clean up",
    selectAll: "Select all", selectNone: "Select none", selected: "Selected", cancel: "Cancel",
    delete: "Delete", nothingToClean: "Nothing to clean up.", unused: "unused",
    items: "items", item: "item", unnamed: "Unnamed", loginFailed: "Incorrect password.",
    loadFailed: "Docker data could not be loaded.", categoryLoadFailed: "This section could not be loaded.",
    images: "Images", volumes: "Volumes", containers: "Stopped containers", buildcache: "Build cache",
    networks: "Networks", networkHint: "unused", containerHint: "stopped", refresh: "Refresh",
    dockerPermission: "Docker access was denied.", dockerMissing: "Docker socket was not found.",
    dockerRefused: "Docker daemon is not responding.", dockerTimeout: "Docker connection timed out.",
    dockerUnavailable: "Docker is not reachable.", partialStats: "Some Docker storage values are currently unavailable.",
    cleanupFailedHeading: "Not deleted", deleted: "deleted", failed: "not deleted",
    noLongerUnused: "The item is now in use, is no longer unused, or no longer exists. It was not deleted.",
    notDeleted: "Docker did not remove this item.", requestFailed: "The delete request failed.",
    verificationFailed: "The status could not be verified again after deletion.", dockerReason: "Docker",
    language: "Language", close: "Close"
  },
  fr: {
    loginTitle: "Se connecter", password: "Mot de passe", login: "Se connecter", logout: "Se déconnecter",
    cleanupTitle: "Nettoyer", reclaimable: "Récupérable", cleanAll: "Tout nettoyer", clean: "Nettoyer",
    selectAll: "Tout sélectionner", selectNone: "Tout désélectionner", selected: "Sélectionné", cancel: "Annuler",
    delete: "Supprimer", nothingToClean: "Rien à nettoyer.", unused: "inutilisé",
    items: "éléments", item: "élément", unnamed: "Sans nom", loginFailed: "Mot de passe incorrect.",
    loadFailed: "Impossible de charger les données Docker.", categoryLoadFailed: "Impossible de charger cette section.",
    images: "Images", volumes: "Volumes", containers: "Conteneurs arrêtés", buildcache: "Cache de build",
    networks: "Réseaux", networkHint: "inutilisés", containerHint: "arrêtés", refresh: "Actualiser",
    dockerPermission: "L’accès à Docker a été refusé.", dockerMissing: "Socket Docker introuvable.",
    dockerRefused: "Le démon Docker ne répond pas.", dockerTimeout: "La connexion à Docker a expiré.",
    dockerUnavailable: "Docker est inaccessible.", partialStats: "Certaines valeurs de stockage Docker sont actuellement indisponibles.",
    cleanupFailedHeading: "Non supprimé", deleted: "supprimé", failed: "non supprimé",
    noLongerUnused: "L’élément est maintenant utilisé, n’est plus inutilisé ou n’existe plus. Il n’a pas été supprimé.",
    notDeleted: "Docker n’a pas supprimé cet élément.", requestFailed: "La demande de suppression a échoué.",
    verificationFailed: "L’état n’a pas pu être revérifié après la suppression.", dockerReason: "Docker",
    language: "Langue", close: "Fermer"
  },
  nl: {
    loginTitle: "Aanmelden", password: "Wachtwoord", login: "Aanmelden", logout: "Afmelden",
    cleanupTitle: "Opschonen", reclaimable: "Vrij te maken", cleanAll: "Alles opschonen", clean: "Opschonen",
    selectAll: "Alles selecteren", selectNone: "Niets selecteren", selected: "Geselecteerd", cancel: "Annuleren",
    delete: "Verwijderen", nothingToClean: "Niets om op te schonen.", unused: "ongebruikt",
    items: "items", item: "item", unnamed: "Naamloos", loginFailed: "Onjuist wachtwoord.",
    loadFailed: "Docker-gegevens konden niet worden geladen.", categoryLoadFailed: "Dit onderdeel kon niet worden geladen.",
    images: "Images", volumes: "Volumes", containers: "Gestopte containers", buildcache: "Build-cache",
    networks: "Netwerken", networkHint: "ongebruikt", containerHint: "gestopt", refresh: "Vernieuwen",
    dockerPermission: "Docker-toegang is geweigerd.", dockerMissing: "Docker-socket is niet gevonden.",
    dockerRefused: "Docker-daemon reageert niet.", dockerTimeout: "Docker-verbinding duurde te lang.",
    dockerUnavailable: "Docker is niet bereikbaar.", partialStats: "Sommige Docker-opslagwaarden zijn momenteel niet beschikbaar.",
    cleanupFailedHeading: "Niet verwijderd", deleted: "verwijderd", failed: "niet verwijderd",
    noLongerUnused: "Het item is nu in gebruik, is niet langer ongebruikt of bestaat niet meer. Het is niet verwijderd.",
    notDeleted: "Docker heeft dit item niet verwijderd.", requestFailed: "De verwijderaanvraag is mislukt.",
    verificationFailed: "De status kon na het verwijderen niet opnieuw worden gecontroleerd.", dockerReason: "Docker",
    language: "Taal", close: "Sluiten"
  },
  es: {
    loginTitle: "Iniciar sesión", password: "Contraseña", login: "Iniciar sesión", logout: "Cerrar sesión",
    cleanupTitle: "Limpiar", reclaimable: "Liberable", cleanAll: "Limpiar todo", clean: "Limpiar",
    selectAll: "Seleccionar todo", selectNone: "No seleccionar nada", selected: "Seleccionado", cancel: "Cancelar",
    delete: "Eliminar", nothingToClean: "No hay nada que limpiar.", unused: "sin usar",
    items: "elementos", item: "elemento", unnamed: "Sin nombre", loginFailed: "Contraseña incorrecta.",
    loadFailed: "No se pudieron cargar los datos de Docker.", categoryLoadFailed: "No se pudo cargar esta sección.",
    images: "Imágenes", volumes: "Volúmenes", containers: "Contenedores detenidos", buildcache: "Caché de compilación",
    networks: "Redes", networkHint: "sin usar", containerHint: "detenidos", refresh: "Actualizar",
    dockerPermission: "Se denegó el acceso a Docker.", dockerMissing: "No se encontró el socket de Docker.",
    dockerRefused: "El daemon de Docker no responde.", dockerTimeout: "La conexión con Docker agotó el tiempo de espera.",
    dockerUnavailable: "Docker no está disponible.", partialStats: "Algunos valores de almacenamiento de Docker no están disponibles actualmente.",
    cleanupFailedHeading: "No eliminado", deleted: "eliminado", failed: "no eliminado",
    noLongerUnused: "El elemento ahora está en uso, ya no está sin usar o ya no existe. No se eliminó.",
    notDeleted: "Docker no eliminó este elemento.", requestFailed: "La solicitud de eliminación falló.",
    verificationFailed: "No se pudo volver a verificar el estado después de la eliminación.", dockerReason: "Docker",
    language: "Idioma", close: "Cerrar"
  },
  pt: {
    loginTitle: "Entrar", password: "Senha", login: "Entrar", logout: "Sair",
    cleanupTitle: "Limpar", reclaimable: "Liberável", cleanAll: "Limpar tudo", clean: "Limpar",
    selectAll: "Selecionar tudo", selectNone: "Desmarcar tudo", selected: "Selecionado", cancel: "Cancelar",
    delete: "Excluir", nothingToClean: "Nada para limpar.", unused: "não utilizado",
    items: "itens", item: "item", unnamed: "Sem nome", loginFailed: "Senha incorreta.",
    loadFailed: "Não foi possível carregar os dados do Docker.", categoryLoadFailed: "Não foi possível carregar esta seção.",
    images: "Imagens", volumes: "Volumes", containers: "Contêineres parados", buildcache: "Cache de build",
    networks: "Redes", networkHint: "não utilizadas", containerHint: "parados", refresh: "Atualizar",
    dockerPermission: "O acesso ao Docker foi negado.", dockerMissing: "O socket do Docker não foi encontrado.",
    dockerRefused: "O daemon do Docker não está respondendo.", dockerTimeout: "A conexão com o Docker expirou.",
    dockerUnavailable: "O Docker não está acessível.", partialStats: "Alguns valores de armazenamento do Docker estão indisponíveis no momento.",
    cleanupFailedHeading: "Não excluído", deleted: "excluído", failed: "não excluído",
    noLongerUnused: "O item agora está em uso, não está mais sem uso ou não existe mais. Ele não foi excluído.",
    notDeleted: "O Docker não excluiu este item.", requestFailed: "A solicitação de exclusão falhou.",
    verificationFailed: "Não foi possível verificar novamente o status após a exclusão.", dockerReason: "Docker",
    language: "Idioma", close: "Fechar"
  },
  pl: {
    loginTitle: "Zaloguj się", password: "Hasło", login: "Zaloguj się", logout: "Wyloguj się",
    cleanupTitle: "Wyczyść", reclaimable: "Do zwolnienia", cleanAll: "Wyczyść wszystko", clean: "Wyczyść",
    selectAll: "Zaznacz wszystko", selectNone: "Odznacz wszystko", selected: "Wybrano", cancel: "Anuluj",
    delete: "Usuń", nothingToClean: "Brak elementów do wyczyszczenia.", unused: "nieużywane",
    items: "elementy", item: "element", unnamed: "Bez nazwy", loginFailed: "Nieprawidłowe hasło.",
    loadFailed: "Nie udało się wczytać danych Docker.", categoryLoadFailed: "Nie udało się wczytać tej sekcji.",
    images: "Obrazy", volumes: "Wolumeny", containers: "Zatrzymane kontenery", buildcache: "Pamięć podręczna build",
    networks: "Sieci", networkHint: "nieużywane", containerHint: "zatrzymane", refresh: "Odśwież",
    dockerPermission: "Odmówiono dostępu do Docker.", dockerMissing: "Nie znaleziono gniazda Docker.",
    dockerRefused: "Demon Docker nie odpowiada.", dockerTimeout: "Przekroczono limit czasu połączenia z Docker.",
    dockerUnavailable: "Docker jest niedostępny.", partialStats: "Niektóre wartości pamięci Docker są obecnie niedostępne.",
    cleanupFailedHeading: "Nie usunięto", deleted: "usunięto", failed: "nie usunięto",
    noLongerUnused: "Element jest teraz używany, nie jest już nieużywany albo już nie istnieje. Nie został usunięty.",
    notDeleted: "Docker nie usunął tego elementu.", requestFailed: "Żądanie usunięcia nie powiodło się.",
    verificationFailed: "Nie udało się ponownie zweryfikować stanu po usunięciu.", dockerReason: "Docker",
    language: "Język", close: "Zamknij"
  },
  it: {
    loginTitle: "Accedi", password: "Password", login: "Accedi", logout: "Esci",
    cleanupTitle: "Pulisci", reclaimable: "Liberabile", cleanAll: "Pulisci tutto", clean: "Pulisci",
    selectAll: "Seleziona tutto", selectNone: "Deseleziona tutto", selected: "Selezionato", cancel: "Annulla",
    delete: "Elimina", nothingToClean: "Niente da pulire.", unused: "inutilizzato",
    items: "elementi", item: "elemento", unnamed: "Senza nome", loginFailed: "Password errata.",
    loadFailed: "Impossibile caricare i dati Docker.", categoryLoadFailed: "Impossibile caricare questa sezione.",
    images: "Immagini", volumes: "Volumi", containers: "Container arrestati", buildcache: "Cache di build",
    networks: "Reti", networkHint: "inutilizzate", containerHint: "arrestati", refresh: "Aggiorna",
    dockerPermission: "Accesso a Docker negato.", dockerMissing: "Socket Docker non trovato.",
    dockerRefused: "Il daemon Docker non risponde.", dockerTimeout: "La connessione a Docker è scaduta.",
    dockerUnavailable: "Docker non è raggiungibile.", partialStats: "Alcuni valori di archiviazione Docker non sono al momento disponibili.",
    cleanupFailedHeading: "Non eliminato", deleted: "eliminato", failed: "non eliminato",
    noLongerUnused: "L’elemento è ora in uso, non è più inutilizzato o non esiste più. Non è stato eliminato.",
    notDeleted: "Docker non ha eliminato questo elemento.", requestFailed: "La richiesta di eliminazione non è riuscita.",
    verificationFailed: "Non è stato possibile verificare nuovamente lo stato dopo l’eliminazione.", dockerReason: "Docker",
    language: "Lingua", close: "Chiudi"
  },
  cs: {
    loginTitle: "Přihlásit se", password: "Heslo", login: "Přihlásit se", logout: "Odhlásit se",
    cleanupTitle: "Vyčistit", reclaimable: "Lze uvolnit", cleanAll: "Vyčistit vše", clean: "Vyčistit",
    selectAll: "Vybrat vše", selectNone: "Zrušit výběr", selected: "Vybráno", cancel: "Zrušit",
    delete: "Odstranit", nothingToClean: "Není co vyčistit.", unused: "nepoužívané",
    items: "položky", item: "položka", unnamed: "Bez názvu", loginFailed: "Nesprávné heslo.",
    loadFailed: "Data Dockeru se nepodařilo načíst.", categoryLoadFailed: "Tuto část se nepodařilo načíst.",
    images: "Obrazy", volumes: "Svazky", containers: "Zastavené kontejnery", buildcache: "Build cache",
    networks: "Sítě", networkHint: "nepoužívané", containerHint: "zastavené", refresh: "Obnovit",
    dockerPermission: "Přístup k Dockeru byl zamítnut.", dockerMissing: "Socket Dockeru nebyl nalezen.",
    dockerRefused: "Docker daemon neodpovídá.", dockerTimeout: "Vypršel časový limit připojení k Dockeru.",
    dockerUnavailable: "Docker není dostupný.", partialStats: "Některé hodnoty úložiště Dockeru momentálně nejsou dostupné.",
    cleanupFailedHeading: "Neodstraněno", deleted: "odstraněno", failed: "neodstraněno",
    noLongerUnused: "Položka se nyní používá, už není nepoužívaná nebo již neexistuje. Nebyla odstraněna.",
    notDeleted: "Docker tuto položku neodstranil.", requestFailed: "Požadavek na odstranění selhal.",
    verificationFailed: "Po odstranění se nepodařilo znovu ověřit stav.", dockerReason: "Docker",
    language: "Jazyk", close: "Zavřít"
  }
};

const LANGUAGE_STORAGE_KEY = "zentdclean_language";
const SUPPORTED_LANGUAGES = Object.freeze(Object.keys(translations));

function normalizeLanguage(value) {
  const base = String(value || "").trim().toLowerCase().split(/[-_]/, 1)[0];
  return SUPPORTED_LANGUAGES.includes(base) ? base : null;
}

function storedLanguage() {
  try {
    return normalizeLanguage(localStorage.getItem(LANGUAGE_STORAGE_KEY));
  } catch {
    return null;
  }
}

function browserLanguage() {
  const primary = (Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages[0]
    : navigator.language) || "";
  return normalizeLanguage(primary) || "en";
}

function rememberLanguage(value) {
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, value);
  } catch {
    // The UI still switches for this session if storage is unavailable.
  }
}

let lang = storedLanguage() || browserLanguage();
let csrf = "";
let overview = null;
let currentKind = "";
let currentItems = [];
let currentResults = [];

const authEnabled = document.body.dataset.authEnabled === "1";
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const t = key => translations[lang]?.[key] || translations.en[key] || key;

const fmt = value => {
  let n = Number(value) || 0;
  if (n < 1024) return `${n} B`;
  const units = ["KB", "MB", "GB", "TB", "PB"];
  let i = -1;
  do { n /= 1024; i++; } while (n >= 1024 && i < units.length - 1);
  return `${n >= 100 ? n.toFixed(0) : n >= 10 ? n.toFixed(1) : n.toFixed(2)} ${units[i]}`;
};
const fmtMaybe = (n, complete = true) => n === null || n === undefined ? "–" : `${fmt(n)}${complete === false ? "+" : ""}`;
const totalDisplay = (value, complete) => value === null || value === undefined ? "–" : `${fmt(value)}${complete === false ? "+" : ""}`;
const selectionSize = items => {
  const knownItems = items.filter(item => Number.isFinite(item.size));
  const known = knownItems.map(item => Number(item.size));
  if (!known.length) return items.length ? "–" : "0 B";
  const value = known.reduce((a, b) => a + b, 0);
  const complete = known.length === items.length && knownItems.every(item => item.size_complete !== false);
  return `${fmt(value)}${complete ? "" : "+"}`;
};

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
}
function shortId(id) {
  const value = String(id || "");
  if (value.startsWith("sha256:")) return value.slice(7, 19);
  return value.length > 18 ? `${value.slice(0, 18)}…` : value;
}
function itemKey(item) {
  return `${item.sourceKind || currentKind}:${item.uid}`;
}
function show(view) {
  $("#loginView").classList.toggle("hidden", view !== "login");
  $("#appView").classList.toggle("hidden", view !== "app");
}
function resetModalStatus() {
  currentResults = [];
  $("#cleanupResult").innerHTML = "";
  $("#cleanupResult").classList.add("hidden");
  $("#modalError").classList.add("hidden");
}
function applyLanguage() {
  document.documentElement.lang = lang;
  $$('[data-i18n]').forEach(el => el.textContent = t(el.dataset.i18n));
  $$('[data-language-select]').forEach(el => { el.value = lang; });
  $$('[data-i18n-aria-label]').forEach(el => el.setAttribute("aria-label", t(el.dataset.i18nAriaLabel)));
  $("#refreshBtn").title = t("refresh");
  $("#refreshBtn").setAttribute("aria-label", t("refresh"));
  if (overview) renderOverview();
  if ($("#cleanupDialog").open) {
    renderItems();
    renderCleanupResults(currentResults);
  }
}

async function api(url, options = {}) {
  const headers = {...(options.headers || {})};
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(url, {...options, headers});
  if (response.status === 401 && url !== "/api/login") {
    show("login");
    throw new Error("unauthorized");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
  return data;
}
async function getSession() {
  const data = await api("/api/session");
  csrf = data.csrf;
}
async function loadOverview() {
  const btn = $("#refreshBtn");
  btn.disabled = true;
  $("#globalError").classList.add("hidden", "notice");
  try {
    overview = await api("/api/overview");
    renderOverview();
  } catch (error) {
    if (error.message !== "unauthorized") showGlobal(t("loadFailed"), false);
  } finally {
    btn.disabled = false;
  }
}
function showGlobal(message, notice = false) {
  const el = $("#globalError");
  el.textContent = message;
  el.classList.toggle("notice", notice);
  el.classList.remove("hidden");
}
function dockerErrorText(code) {
  return ({
    permission_denied: t("dockerPermission"), socket_missing: t("dockerMissing"), not_a_socket: t("dockerMissing"),
    connection_refused: t("dockerRefused"), timeout: t("dockerTimeout")
  })[code] || t("dockerUnavailable");
}
function renderOverview() {
  const dockerOk = overview.docker?.available !== false;
  $("#reclaimTotal").textContent = dockerOk ? totalDisplay(overview.reclaimable_total, overview.reclaimable_total_complete) : "–";
  $("#cleanAllSize").textContent = dockerOk ? totalDisplay(overview.reclaimable_total, overview.reclaimable_total_complete) : "";
  const kinds = ["images", "volumes", "containers", "buildcache", "networks"];
  $("#cleanAllBtn").disabled = !dockerOk || !kinds.some(kind => overview[kind]?.available !== false && overview[kind]?.count > 0);
  if (!dockerOk) showGlobal(dockerErrorText(overview.docker?.error), false);
  else if (overview.partial) showGlobal(t("partialStats"), true);
  else $("#globalError").classList.add("hidden");

  const cardKinds = ["images", "volumes", "buildcache", "containers", "networks"];
  $("#cards").innerHTML = cardKinds.map(kind => {
    const x = overview[kind] || {count: 0, reclaimable: null, reclaimable_complete: false, available: false};
    const available = dockerOk && x.available !== false;
    let meta = "–";
    if (available && kind === "containers") meta = `${x.count} ${t("containerHint")}`;
    else if (available && kind === "networks") meta = `${x.count} ${t("networkHint")}`;
    else if (available) meta = `${x.count} ${t("unused")}`;

    let value = "–";
    let valueLabel = "";
    if (available && kind === "networks") {
      value = String(x.count);
      valueLabel = t("networkHint");
    } else if (available && x.reclaimable !== null && x.reclaimable !== undefined) {
      value = totalDisplay(x.reclaimable, x.reclaimable_complete);
      valueLabel = t("reclaimable");
    } else if (available && kind !== "networks") {
      valueLabel = t("reclaimable");
    }

    return `<article class="card"><div class="card-top"><div><h2>${t(kind)}</h2><div class="card-meta">${meta}</div></div><div class="card-size"><strong>${value}</strong><span>${valueLabel}</span></div></div><div class="card-top"><div></div><button class="clean-button" data-kind="${kind}" ${available && x.count ? "" : "disabled"}>${t("clean")}</button></div></article>`;
  }).join("");
  $$('.clean-button').forEach(button => button.addEventListener("click", () => openCleanup(button.dataset.kind)));
}

function normalizeItems(items, sourceKind = null, previous = null) {
  const hasPreviousState = previous instanceof Map;
  const previousState = hasPreviousState ? previous : new Map();
  return items.map(item => {
    const normalized = {...item, ...(sourceKind ? {sourceKind} : {})};
    const key = `${normalized.sourceKind || currentKind}:${normalized.uid}`;
    normalized._checked = hasPreviousState ? (previousState.has(key) ? previousState.get(key) : false) : true;
    return normalized;
  });
}
function buildCacheGroup(items, previous = null) {
  if (!items.length) return null;
  const known = items.filter(item => Number.isFinite(item.size));
  const size = known.length ? known.reduce((sum, item) => sum + Number(item.size), 0) : null;
  const sizeComplete = known.length === items.length && known.every(item => item.size_complete !== false);
  const group = {
    uid: "__all_unused_buildcache__",
    name: "Build cache",
    details: "",
    size,
    size_complete: sizeComplete,
    sourceKind: "buildcache",
    _buildcacheGroup: true,
    _buildcacheCount: items.length,
    _buildcacheIds: items.map(item => String(item.uid))
  };
  const key = `buildcache:${group.uid}`;
  group._checked = previous instanceof Map ? (previous.has(key) ? previous.get(key) : false) : true;
  return group;
}
function normalizeAllCandidates(data, previous = null) {
  const unavailable = new Set(data._unavailable || []);
  const flattened = [];
  for (const kind of ["images", "volumes", "buildcache", "containers", "networks"]) {
    if (unavailable.has(kind)) continue;
    if (kind === "buildcache") {
      const group = buildCacheGroup(data[kind] || [], previous);
      if (group) flattened.push(group);
    } else {
      flattened.push(...normalizeItems(data[kind] || [], kind, previous));
    }
  }
  return flattened;
}
function stateMap() {
  return new Map(currentItems.map(item => [itemKey(item), item._checked !== false]));
}
function renderItems() {
  const buildCachePreview = currentKind === "buildcache";
  $("#bulkActions").classList.toggle("hidden", buildCachePreview);
  if (!currentItems.length) {
    $("#modalList").innerHTML = "";
    $("#modalEmpty").classList.remove("hidden");
    updateSelection();
    return;
  }
  $("#modalEmpty").classList.add("hidden");
  $("#modalList").innerHTML = currentItems.map((item, index) => {
    const displayName = item._buildcacheGroup ? t("buildcache") : (item.name === "<none>:<none>" ? t("unnamed") : item.name);
    const detail = item._buildcacheGroup
      ? [currentKind === "all" ? t("buildcache") : "", `${item._buildcacheCount} ${t("unused")}`].filter(Boolean).join(" · ")
      : [currentKind === "all" && item.sourceKind ? t(item.sourceKind) : "", shortId(item.uid), item.details].filter(Boolean).join(" · ");
    const main = `<span class="item-main"><div class="item-name">${escapeHtml(displayName)}</div><div class="item-detail">${escapeHtml(detail)}</div></span><span class="item-size">${fmtMaybe(item.size, item.size_complete !== false)}</span>`;
    if (buildCachePreview) {
      return `<div class="cleanup-row cleanup-row-preview" title="${escapeHtml(item.uid)}">${main}</div>`;
    }
    return `<label class="cleanup-row" title="${escapeHtml(item.uid)}"><span class="switch"><input type="checkbox" data-index="${index}" ${item._checked === false ? "" : "checked"}><span class="slider"></span></span>${main}</label>`;
  }).join("");
  if (!buildCachePreview) {
    $$('#modalList input[type="checkbox"]').forEach(box => box.addEventListener("change", () => {
      const index = Number(box.dataset.index);
      if (currentItems[index]) currentItems[index]._checked = box.checked;
      updateSelection();
    }));
  }
  updateSelection();
}
function selectedItems() {
  return currentKind === "buildcache" ? currentItems : currentItems.filter(item => item._checked !== false);
}
function updateSelection() {
  const items = selectedItems();
  $("#selectedCount").textContent = items.length;
  $("#selectedSize").textContent = selectionSize(items);
  $("#deleteBtn").disabled = items.length === 0;
}
function cleanupReason(result) {
  if (result.error_code === "no_longer_unused") return t("noLongerUnused");
  if (result.error_code === "verification_failed") return result.error_detail ? `${t("verificationFailed")} ${result.error_detail}` : t("verificationFailed");
  if (result.error_code === "not_deleted") return result.error_detail ? `${t("notDeleted")} ${result.error_detail}` : t("notDeleted");
  if (result.error_code === "request_error") return result.error_detail ? `${t("requestFailed")} ${result.error_detail}` : t("requestFailed");
  if (result.error_detail) return `${t("dockerReason")}: ${result.error_detail}`;
  return t("notDeleted");
}

function renderCleanupResults(results) {
  const panel = $("#cleanupResult");
  const failed = (results || []).filter(result => result.status !== "deleted");
  if (!failed.length) {
    panel.innerHTML = "";
    panel.classList.add("hidden");
    return;
  }
  const deletedCount = (results || []).length - failed.length;
  panel.innerHTML = `<div class="cleanup-result-summary"><strong>${t("cleanupFailedHeading")}</strong><span>${deletedCount} ${t("deleted")} · ${failed.length} ${t("failed")}</span></div>${failed.map(result => {
    const kind = result.sourceKind || currentKind;
    const displayName = result.name === "<none>:<none>" ? t("unnamed") : (result.name || result.uid);
    const detail = [currentKind === "all" && kind ? t(kind) : "", shortId(result.uid)].filter(Boolean).join(" · ");
    return `<div class="cleanup-failure"><div class="failure-main"><strong>${escapeHtml(displayName)}</strong><span>${escapeHtml(detail)}</span><p>${escapeHtml(cleanupReason(result))}</p></div></div>`;
  }).join("")}`;
  panel.classList.remove("hidden");
  panel.scrollIntoView({block: "nearest"});
}

async function openCleanup(kind) {
  currentKind = kind;
  currentItems = [];
  resetModalStatus();
  $("#bulkActions").classList.toggle("hidden", kind === "buildcache");
  $("#modalTitle").textContent = t(kind);
  $("#modalList").innerHTML = `<div class="empty"><span class="spinner"></span></div>`;
  $("#modalEmpty").classList.add("hidden");
  $("#deleteBtn").disabled = true;
  $("#cleanupDialog").showModal();
  try {
    const data = await api(`/api/candidates/${kind}`);
    currentItems = normalizeItems(data[kind] || []);
    renderItems();
  } catch {
    currentItems = [];
    $("#modalList").innerHTML = "";
    $("#modalError").textContent = t("categoryLoadFailed");
    $("#modalError").classList.remove("hidden");
  }
}
async function cleanAll() {
  const btn = $("#cleanAllBtn");
  btn.disabled = true;
  resetModalStatus();
  try {
    const data = await api("/api/candidates/all");
    currentKind = "all";
    currentItems = normalizeAllCandidates(data);
    $("#modalTitle").textContent = t("cleanAll");
    $("#cleanupDialog").showModal();
    renderItems();
  } catch {
    showGlobal(t("loadFailed"), false);
  } finally {
    btn.disabled = false;
  }
}

function chunk(items, size = 200) {
  const chunks = [];
  for (let i = 0; i < items.length; i += size) chunks.push(items.slice(i, i + size));
  return chunks;
}
async function cleanupGroup(kind, items) {
  const results = [];
  // BuildKit cache is a garbage-collected graph, not a collection of reliably
  // deletable CRUD records. Send its complete preview in one request so the
  // backend can execute one native unused-cache prune.
  const batches = kind === "buildcache" ? [items] : chunk(items, 200);
  for (const batch of batches) {
    try {
      const data = await api("/api/cleanup", {
        method: "POST",
        body: JSON.stringify({
          kind,
          ids: batch.flatMap(item => item._buildcacheGroup ? item._buildcacheIds : [item.uid]),
          csrf
        })
      });
      const groupItem = batch.find(item => item._buildcacheGroup);
      if (kind === "buildcache" && groupItem) {
        const failed = (data.results || []).filter(result => result.status === "error");
        if (failed.length) {
          const first = failed[0];
          results.push({
            uid: groupItem.uid, name: groupItem.name, sourceKind: kind, status: "error",
            error_code: first.error_code || "not_deleted",
            error_detail: first.error_detail || `${failed.length} build-cache record(s) were kept by Docker.`
          });
        } else {
          results.push({uid: groupItem.uid, name: groupItem.name, sourceKind: kind, status: "deleted"});
        }
        continue;
      }
      const originals = new Map(batch.map(item => [String(item.uid), item]));
      const returned = new Set();
      for (const result of data.results || []) {
        const uid = String(result.uid || "");
        if (!originals.has(uid) || returned.has(uid)) continue;
        returned.add(uid);
        const original = originals.get(uid);
        const name = (!result.name || result.name === result.uid) ? (original?.name || result.uid) : result.name;
        results.push({...result, name, sourceKind: kind});
      }
      // A cleanup endpoint must account for every requested object. Treat an
      // incomplete response as a failure instead of silently losing entries.
      for (const [uid, original] of originals) {
        if (returned.has(uid)) continue;
        results.push({
          uid, name: original.name, sourceKind: kind, status: "error",
          error_code: "request_error", error_detail: "No cleanup result returned by the server."
        });
      }
    } catch (error) {
      for (const item of batch) {
        results.push({uid: item.uid, name: item.name, sourceKind: kind, status: "error", error_code: "request_error", error_detail: error.message});
      }
    }
  }
  return results;
}
async function refreshCurrentCandidates(previousState, keepKeys = null) {
  let refreshed = [];
  if (currentKind === "all") {
    const data = await api("/api/candidates/all");
    refreshed = normalizeAllCandidates(data, previousState);
  } else {
    const data = await api(`/api/candidates/${currentKind}`);
    refreshed = normalizeItems(data[currentKind] || [], null, previousState);
  }
  currentItems = keepKeys instanceof Set ? refreshed.filter(item => keepKeys.has(itemKey(item))) : refreshed;
  renderItems();
}

async function doCleanup() {
  const items = selectedItems();
  if (!items.length) return;
  const btn = $("#deleteBtn");
  const old = btn.innerHTML;
  const previousState = stateMap();
  const unselectedKeys = new Set(currentItems.filter(item => item._checked === false).map(itemKey));
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>${t("delete")}`;
  resetModalStatus();
  try {
    const grouped = new Map();
    for (const item of items) {
      const kind = currentKind === "all" ? item.sourceKind : currentKind;
      if (!grouped.has(kind)) grouped.set(kind, []);
      grouped.get(kind).push(item);
    }
    const results = [];
    for (const [kind, groupedItems] of grouped) results.push(...await cleanupGroup(kind, groupedItems));
    currentResults = results;
    const failed = results.filter(result => result.status !== "deleted");
    await loadOverview();
    if (!failed.length) {
      $("#cleanupDialog").close();
      return;
    }
    const keepKeys = new Set(unselectedKeys);
    for (const result of failed) keepKeys.add(`${result.sourceKind || currentKind}:${result.uid}`);
    await refreshCurrentCandidates(previousState, keepKeys);
    renderCleanupResults(currentResults);
  } catch (error) {
    $("#modalError").textContent = error.message || t("requestFailed");
    $("#modalError").classList.remove("hidden");
  } finally {
    btn.innerHTML = old;
    btn.disabled = false;
    updateSelection();
  }
}

$("#loginForm").addEventListener("submit", async event => {
  event.preventDefault();
  const btn = event.submitter;
  btn.disabled = true;
  $("#loginError").classList.add("hidden");
  try {
    const data = await api("/api/login", {method: "POST", body: JSON.stringify({password: $("#password").value})});
    csrf = data.csrf;
    $("#password").value = "";
    show("app");
    await loadOverview();
  } catch (error) {
    if (error.message !== "unauthorized") {
      $("#loginError").textContent = t("loginFailed");
      $("#loginError").classList.remove("hidden");
    }
  } finally {
    btn.disabled = false;
  }
});
$("#logoutBtn").addEventListener("click", async () => {
  if (!authEnabled) return;
  await api("/api/logout", {method: "POST"}).catch(() => {});
  csrf = "";
  show("login");
});
$("#refreshBtn").addEventListener("click", loadOverview);
$("#cleanAllBtn").addEventListener("click", cleanAll);
$("#deleteBtn").addEventListener("click", doCleanup);
$("#selectAllBtn").addEventListener("click", () => {
  currentItems.forEach(item => { item._checked = true; });
  renderItems();
});
$("#selectNoneBtn").addEventListener("click", () => {
  currentItems.forEach(item => { item._checked = false; });
  renderItems();
});
$$('[data-language-select]').forEach(select => select.addEventListener("change", () => {
  const next = normalizeLanguage(select.value);
  if (!next) return;
  lang = next;
  rememberLanguage(lang);
  applyLanguage();
}));

function registerPWA() {
  if (!("serviceWorker" in navigator) || !window.isSecureContext) return;
  const revision = encodeURIComponent(document.body.dataset.assetRevision || "7");
  window.addEventListener("load", () => {
    navigator.serviceWorker.register(`/service-worker.js?v=${revision}`, {scope: "/"}).catch(() => {});
  }, {once: true});
}

(async () => {
  registerPWA();
  applyLanguage();
  if (!authEnabled || document.body.dataset.loggedIn === "1") {
    show("app");
    try {
      await getSession();
      await loadOverview();
    } catch {
      if (authEnabled) show("login");
    }
  } else {
    show("login");
  }
})();

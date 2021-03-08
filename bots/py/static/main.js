// Returns a function, that, when invoked, will only be triggered at most once
// during a given window of time. Normally, the throttled function will run
// as much as it can, without ever going more than once per `wait` duration;
// but if you'd like to disable the execution on the leading edge, pass
// `{leading: false}`. To disable execution on the trailing edge, ditto.
function throttle(func, wait, options) {
    var context, args, result
    var timeout = null
    var previous = 0
    if (!options) options = {}
    var later = function () {
        previous = options.leading === false ? 0 : Date.now()
        timeout = null
        result = func.apply(context, args)
        if (!timeout) context = args = null
    }
    return function () {
        var now = Date.now()
        if (!previous && options.leading === false) previous = now
        var remaining = wait - (now - previous)
        context = this
        args = arguments
        if (remaining <= 0 || remaining > wait) {
            if (timeout) {
                clearTimeout(timeout)
                timeout = null
            }
            previous = now
            result = func.apply(context, args)
            if (!timeout) context = args = null
        } else if (!timeout && options.trailing !== false) {
            timeout = setTimeout(later, remaining)
        }
        return result
    }
}

// Main code

const Modes = {
    TABLE: 'TABLE',
    CARDS: 'CARDS',
}
const START_TYPING = 'Start typing to see results!'
const NO_RESULTS = 'No results found. Try something else!'

const inputEl = document.querySelector('input')
const resultsEl = document.querySelector('.results')
const cardsEl = document.querySelector('.cards-container')
const tbodyEl = document.querySelector('tbody')
const searchInfoEl = document.querySelector('.search-info')

let mode = Modes.CARDS
let data
let searchQuery = new URLSearchParams(window.location.search).get('q') || ''

const isValidQuery = () => searchQuery && searchQuery.length > 2

async function getData(query) {
    const response = await fetch(`/api/stats/search?q=${query}`)

    if (!response.ok) return false

    return response.json()
}

function setUrlParam(key, value) {
    if (history.replaceState) {
        const searchParams = new URLSearchParams(window.location.search)
        searchParams.set(key, value)

        const newUrl =
            window.location.protocol +
            '//' +
            window.location.host +
            window.location.pathname +
            '?' +
            searchParams.toString()
        window.history.replaceState({ path: newUrl }, '', newUrl)
    }
}

function renderCard(major) {
    const div = document.createElement('div')

    div.className = 'card'
    div.innerHTML = `
        <h2 class="campus">${major.Campus}</h2>
        <h2>${major.Major}</h2>
        <div>
            <div class="data">
                <div class="item">
                    <div class="value">${major.Applicants}</div>
                    <div class="label">Apply</div>
                </div>
                <div class="item">
                    <!-- <div class="value">${major.Admits} <span style="color: #999">${major['Admit rate']}</span></div> -->
                    <div class="value">${major.Admits} (${major['Admit rate']})</div>
                    <!-- <div class="value">${major.Admits} <span style="color: #999">·</span> ${major['Admit rate']}</div>
                    <div class="value">${major.Admits}</div> -->
                    <div class="label">Admitted</div>
                </div>
                <div class="item">
                    <div class="value">${major.Enrolls}</div>
                    <div class="label">Enroll</div>
                </div>
            </div>
            <div class="data" style="justify-content: center;">
                <!--
                <div class="item">
                    <div class="value">${major['Admit rate']}</div>
                    <div class="label">Admit Rate</div>
                </div>
                -->
                <div class="item gpa-range">
                    <div class="value">${major['Admit GPA range']}</div>
                    <div class="label">Admit GPA Range</div>
                </div>
            </div>
        </div>
    `

    return div
}

function renderTableRow(major) {
    const tr = document.createElement('tr')

    tr.innerHTML = `
        <td class="left">${major.Campus}</td>
        <td class="left">${major.Major}</td>
        <td>${major.Applicants}</td>
        <td>${major.Admits}</td>
        <td>${major.Enrolls}</td>
        <td>${major['Admit rate']}</td>
        <td>${major['Admit GPA range']}</td>
    `

    return tr
}

function showMessage(text) {
    searchInfoEl.textContent = text
    searchInfoEl.classList.add('visible')
}

async function doUpdate() {
    resultsEl.dataset.mode = mode

    const targetEl = mode == Modes.TABLE ? tbodyEl : cardsEl

    if (!isValidQuery()) {
        targetEl.innerHTML = ''
        targetEl.style.display = 'none'
        showMessage(START_TYPING)
        return
    }

    if (!data || !data.length) {
        targetEl.innerHTML = ''
        targetEl.style.display = 'none'
        showMessage(NO_RESULTS)
        return
    }

    targetEl.style.display = ''
    searchInfoEl.classList.remove('visible')

    const fragment = document.createDocumentFragment()
    const isMobile = window.matchMedia
        ? window.matchMedia('(max-width: 600px)').matches
        : false
    const maxItemIdx = isMobile ? Math.min(data.length, 10) : data.length

    for (let i = 0; i < maxItemIdx; i++) {
        const major = data[i]

        fragment.appendChild(
            mode == Modes.TABLE ? renderTableRow(major) : renderCard(major)
        )
    }

    targetEl.innerHTML = ''
    targetEl.appendChild(fragment)
}

async function fetchAndUpdate() {
    setUrlParam('q', searchQuery)

    const targetEl = mode == Modes.TABLE ? tbodyEl : cardsEl

    if (isValidQuery()) {
        data = await getData(searchQuery)
    }

    doUpdate()
}

inputEl.addEventListener(
    'input',
    throttle(
        async (event) => {
            searchQuery = event.target.value
            await fetchAndUpdate()
        },
        400,
        { leading: false }
    )
)

const tableButton = document.getElementById('table-btn')

tableButton.addEventListener('click', () => {
    if (mode != Modes.TABLE) {
        mode = Modes.TABLE
        tableButton.classList.add('on')
    } else {
        mode = Modes.CARDS
        tableButton.classList.remove('on')
    }

    doUpdate()
})

// on first load
inputEl.value = searchQuery
fetchAndUpdate()

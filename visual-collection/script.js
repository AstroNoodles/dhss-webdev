// Michael Batavia - JS Code for Flight API Query

let codeImageDict = {
    'LH': 'airline-logos/lufthansa.png',
    'EN': 'airline-logos/airdolomiti.png',
    'LX': 'airline-logos/swiss.png',
    'AZ': 'airline-logos/ita.png',
    '4Y': 'airline-logos/discover.png',
    'OS': 'airline-logos/austrian.png',
    'WK': 'airline-logos/edelweiss.png',
    'EW': 'airline-logos/eurowings.png'
}

let inactiveList = []
let layerGroup = L.layerGroup()


// Utility function to reverse lookup a dictionary
function reverseLookup(obj, value) {
    return Object.keys(obj).find(key => obj[key] === value) || null;
}

function setUpMap() {
    var map = L.map('map').setView([48.126, 11.55], 13)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    return map
}

async function convertCodeToAirportName(flightCode, map) {
    const airportsURL = 'https://raw.githubusercontent.com/AstroNoodles/dhss-webdev/refs/heads/main/visual-collection/airports.csv'
    const airportsList = await fetch(airportsURL)
    let data = await airportsList.text()

    const parsedData = Papa.parse(data, {
        header: true,
        skipEmptyLines: true
    })

    //console.log(parsedData)

    for(let i = 0; i < parsedData.data.length; i++) {
        let row = parsedData.data[i]
        console.log(`IATA Code: ${row['IATA Code']}`)
        console.log(`Flight Code: ${flightCode}`)
        if(row['IATA Code'] === flightCode) {
            console.log('a match!')
            console.log([row['Latitude'], row['Longitude']])

            return {
                'Airport Name': row['Airport Name'],
                'Longitude': row['Longitude'],
                'Latitude': row['Latitude']    
            }
        }
    }

    console.log('no matches found')
    return {
        'Airport Name': 'Airport',
        'Longitude': 55,
        'Latitude': -17
    }
}

async function updateFlightBox(map) {
    let flightBox = document.querySelector(".codelist")
    const flightsURL = 'https://raw.githubusercontent.com/AstroNoodles/dhss-webdev/refs/heads/main/visual-collection/interesting_flights.txt'
    try {
        const response = await fetch(flightsURL)
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}, ${response.statusText}`);
        } else {
            // do stuff
            let flights = await response.text()
            console.log(flights)

            let cleanedFlightsArr = flights.split("\n")
            console.log(cleanedFlightsArr)

            cleanedFlightsArr.forEach((flightCode) => {
                let cleanedFlightCode = flightCode.substring(0, 6).replace(" ", "")
                let airlineCode = flightCode.substring(0, 2)
                console.log(airlineCode)

                if (Object.keys(codeImageDict).includes(airlineCode)) {
                    let flightCodeBox = document.createElement('div')
                    let flightCodeText = document.createElement('p')

                    flightCodeText.textContent = cleanedFlightCode
                    flightCodeText.className = 'code'
                    flightCodeBox.className = 'code-button'

                    flightCodeBox.addEventListener('click', (e) => {
                        let prevDate = new Date();
                        prevDate.setDate(prevDate.getDate() - 1)

                        const isoFormatter = new Intl.DateTimeFormat('en-CA', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                        })

                        fetchFlightStatus(cleanedFlightCode, flightCodeBox, isoFormatter.format(prevDate), map)
                    })

                    flightCodeBox.appendChild(flightCodeText)
                    flightBox.appendChild(flightCodeBox)
                }
            })
        }
    } catch (error) {
        console.error(error)
    }
}

// Fetches Flight Status from Lufthansa Group UI and Updates UI
async function fetchFlightStatus(flightCode, flightCodeBox, flightDate, map) {
    const url = `https://customer-flight-info.p-eu.rapidapi.com/customerflightinformation/${flightCode}/${flightDate}`;
    // const urlD = `https://customer-flight-info.p-eu.rapidapi.com/customerflightinformation/${flightCode}/2025-04-05`;
    
    console.log(url)

    // in future, need to remove secret key...
    const options = {
        method: 'GET',
        headers: {
            Authorization: 'Bearer uxgnnb25wsu9v8chss6qdqm8',
            'X-RapidAPI-Key': '3797d19498msh35809fc55e6fb25p1cc76ejsnbdcd51c7e0eb',
            'X-RapidAPI-Host': 'customer-flight-info.iata.rapidapi.com'
          }
        }  

    try {
        const response = await fetch(url, options);

        let chosenFlightHeader = document.getElementById('chosen-flight-header')
        let chosenFlightImage = document.getElementById('chosen-flight-image')

        let fromCode = document.getElementById('from-header')
        let toCode = document.getElementById('to-header')
        let fromPlace = document.getElementById('from-place')
        let toPlace = document.getElementById('to-place')
        let fromTerm = document.getElementById('from-terminal')
        let toTerm = document.getElementById('to-terminal')
        let fromDate = document.getElementById('from-date')
        let toDate = document.getElementById('to-date')
        let fromTime = document.getElementById('from-time')
        let toTime = document.getElementById('to-time')
        let fromStatus = document.getElementById('from-status')
        let toStatus = document.getElementById('to-status')

        let progressBar = document.getElementById('flight-progress')
        let flightTime = document.getElementById('flight-time')
        let flightRemaining = document.getElementById('flight-remaining')

        if (!response.ok) {
            console.log(new Error(`Response status: ${response.status}, ${response.statusText}`))
            flightCodeBox.classList.add('code-button-disabled')
            chosenFlightHeader.classList.add('error-header')

            if(fromPlace.classList.contains('airports')) {
                fromPlace.classList.remove('airports')
                toPlace.classList.remove('airports')
            }

            // Error information
            let airlineCode = flightCode.substring(0, 2)
            chosenFlightImage.src = codeImageDict[airlineCode]
            
            chosenFlightHeader.textContent = `No flight can be found for this flight code. Try again later!`
            fromCode.textContent = `XXX`
            toCode.textContent = `XXX`
            fromPlace.textContent = 'Unavailable'
            toPlace.textContent = 'Unavailable'
            fromTerm.textContent = `TERMINAL UNAVAILABLE`
            toTerm.textContent = `TERMINAL UNAVAILABLE`
            fromDate.textContent = `Apr-2025`
            toDate.textContent = `Apr-2025`
            fromTime.textContent = `X:XX PM`
            toTime.textContent = `X:XX PM`
            toStatus.textContent = `ONTIME`

            progressBar.value = "0"
            flightTime.textContent = `INFINITY HOURS INFINITY MINUTES`
            flightRemaining.textContent = `INFINITY HOURS INFINITY MINUTES`

            inactiveList.push(flightCode)

        } else {
            let flightInfo = await response.json()
            console.log(flightInfo)

            let airlineCode = flightCode.substring(0, 2)
            let mainFlightInfo = flightInfo['FlightInformation']['Flights']['Flight']

            // Remove the red color from header if previous list item was erroneous code
            if(chosenFlightHeader.classList.contains('error-header')) {
                chosenFlightHeader.classList.remove('error-header')
            }


            // HEADER AND FLIGHT CARRIER INFO
            chosenFlightHeader.textContent = flightCode
            chosenFlightImage.src = codeImageDict[airlineCode]
            fromCode.textContent = mainFlightInfo['Departure']['AirportCode']
            toCode.textContent = mainFlightInfo['Arrival']['AirportCode']

            // TERMINAL INFO
            let terminalInfoD = mainFlightInfo['Departure']['Terminal']

            if(!mainFlightInfo['Departure'].hasOwnProperty('Terminal')) {
                fromTerm.textContent = 'TERMINAL'
            } else {
                if (terminalInfoD.hasOwnProperty('Name') && terminalInfoD.hasOwnProperty('Gate')) {
                    fromTerm.textContent = `TERMINAL ${terminalInfoD['Name']} - GATE ${terminalInfoD['Gate']}`
                } else if (terminalInfoD.hasOwnProperty('Name')) {
                    fromTerm.textContent = `TERMINAL ${terminalInfoD['Name']}`
                } else if (terminalInfoD.hasOwnProperty('Gate')) {
                    fromTerm.textContent = `GATE ${terminalInfoD['Gate']}`
                } else {
                    fromTerm.textContent = 'TERMINAL'
                }
            }

            // TERMINAL INFO
            let terminalInfoA = mainFlightInfo['Arrival']['Terminal']

            if(!mainFlightInfo['Arrival'].hasOwnProperty('Terminal')) {
                toTerm.textContent = 'TERMINAL'
            } else {
                if (terminalInfoA.hasOwnProperty('Name') && terminalInfoA.hasOwnProperty('Gate')) {
                    toTerm.textContent = `TERMINAL ${terminalInfoA['Name']} - GATE ${terminalInfoA['Gate']}`
                } else if (terminalInfoA.hasOwnProperty('Name')) {
                    toTerm.textContent = `TERMINAL ${terminalInfoA['Name']}`
                } else if (terminalInfoA.hasOwnProperty('Gate')) {
                    toTerm.textContent = `GATE ${terminalInfoA['Gate']}`
                } else {
                    toTerm.textContent = 'TERMINAL'
                }
            }

            // Place Name Info
            let fromAirport = await convertCodeToAirportName(mainFlightInfo['Departure']['AirportCode'], map)
            let toAirport = await convertCodeToAirportName(mainFlightInfo['Arrival']['AirportCode'], map)

            console.log('now we are here!')
            fromPlace.textContent = fromAirport['Airport Name']
            toPlace.textContent = toAirport['Airport Name']

            let latLngCoords = [
                [fromAirport['Latitude'], fromAirport['Longitude']],
                [toAirport['Latitude'], toAirport['Longitude']]
            ]

            layerGroup.clearLayers()

            var fromMarker = L.marker([fromAirport['Latitude'], fromAirport['Longitude']])
            var toMarker = L.marker([toAirport['Latitude'], toAirport['Longitude']])
            // let polyline = L.polyline(latLngCoords, {color: 'red'}).addTo(map)

            const arc = new L.Polyline.Arc(latLngCoords[0], latLngCoords[1], {
                color: 'blue',
                weight: 3,
                vertices: 100  // smoother curve with more points
            })

            layerGroup.addLayer(fromMarker)
            layerGroup.addLayer(toMarker)
            layerGroup.addLayer(arc)

            layerGroup.addTo(map)

            map.fitBounds(arc.getBounds())

            fromPlace.classList.add('airports')
            toPlace.classList.add('airports')

            // DATE INFO
            fromDate.textContent = mainFlightInfo['Departure']['Actual']['Date']
            toDate.textContent = mainFlightInfo['Arrival']['Actual']['Date']
            fromTime.textContent = mainFlightInfo['Departure']['Actual']['Time']
            toTime.textContent = mainFlightInfo['Arrival']['Actual']['Time']

            // STATUS INFO
            let scheduledDepartureTime = mainFlightInfo['Departure']['Scheduled']['Time']
            let actualDepartureTime = mainFlightInfo['Departure']['Actual']['Time']
            let scheduledDeparture = new Date(`${flightDate}T${scheduledDepartureTime}`)
            let actualDeparture = new Date(`${flightDate}T${actualDepartureTime}`)

            let scheduledArrivalTime = mainFlightInfo['Arrival']['Scheduled']['Time']
            let actualArrivalTime = mainFlightInfo['Arrival']['Actual']['Time']
            let scheduledArrival = new Date(`${flightDate}T${scheduledArrivalTime}`)
            let actualArrival = new Date(`${flightDate}T${actualArrivalTime}`)

            let numericStatusD = (actualDeparture.getTime() - scheduledDeparture.getTime()) / 1000
            let numericStatusA = (actualArrival.getTime() - scheduledArrival.getTime()) / 1000

            let statusD = ''
            let statusA = ''

            if (numericStatusD < 0) {
                statusD = 'EARLY'
                fromStatus.textContent = `${Math.abs(Math.floor(numericStatusD / 60))} MINUTES ${statusD}`
            } else if (numericStatusD > 0) {
                statusD = 'LATE'
                fromStatus.textContent = `${Math.floor(numericStatusD / 60)} MINUTES ${statusD}`
            } else fromStatus.textContent = 'ON TIME'

            if (numericStatusA < 0) {
                statusA = 'EARLY'
                toStatus.textContent = `${Math.abs(Math.floor(numericStatusD / 60))} MINUTES ${statusA}`
            } else if (numericStatusA > 0) {
                statusA = 'LATE'
                toStatus.textContent = `${Math.floor(numericStatusD / 60)} MINUTES ${statusA}`
            } else toStatus.textContent = 'ON TIME'

            // FLIGHT TIME INFORMATION
            if (mainFlightInfo['Status']['Code'] === 'LD') {
                let secTaken = (actualArrival.getTime() - actualDeparture.getTime()) / 1000
                let minTaken = (secTaken / 60) % 60
                let hoursTaken = secTaken / 3600 
                console.log(secTaken / 60)
                console.log(secTaken / 3600)

                console.log(minTaken)
                console.log(hoursTaken)

                let displayHours = Math.abs(Math.floor(hoursTaken))
                let displayMin = Math.abs(Math.floor(minTaken))
                progressBar.value = "100"

                flightTime.textContent = `${displayHours} HOURS, ${displayMin} MINUTES`
                flightRemaining.textContent = `0 HOURS 0 MINUTES`
            }

            
        }

    } catch (error) {
        console.error(error);
    }

}

// MAIN functionality
let sidebarButton = document.querySelector('#sidebar-button')
let sidebar = document.querySelector('.sidebar');
let buttonIcon = document.querySelector('#sidebar-btn-img');

console.log(sidebarButton)
console.log(sidebar)
console.log(buttonIcon)

let map = setUpMap()
updateFlightBox(map)

sidebarButton.addEventListener('click', (e) => {
    let prevDisplayStyle = sidebar.style.display;
    if (prevDisplayStyle === 'none') {
        sidebar.style.display = 'block';
        buttonIcon.src = 'double-arrow-down.png'
    } else {
        sidebar.style.display = 'none';
        buttonIcon.src = 'double-arrow-right.png'
    }
})

window.addEventListener('beforeunload', (event) => {
    console.log("Remove these codes in future installments")
    console.log(inactiveList)
    alert(`Remove these codes: ${inactiveList}`)
})









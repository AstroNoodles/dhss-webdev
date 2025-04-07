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

async function fetchFlightStatus(flightCode, flightCodeBox, flightDate) {
    const url = `https://customer-flight-info.p-eu.rapidapi.com/customerflightinformation/${flightCode}/${flightDate}`;
    console.log(url)

    // in future, need to remove secret key...
    const options = {
        method: 'GET',
        headers: {
            Authorization: 'Bearer 2q5y7r5tvq6e53yvjkx6mge6',
            'X-RapidAPI-Key': '3797d19498msh35809fc55e6fb25p1cc76ejsnbdcd51c7e0eb',
            'X-RapidAPI-Host': 'customer-flight-info.iata.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            console.log(new Error(`Response status: ${response.status}, ${response.statusText}`))
            flightCodeBox.classList.add('code-button-disabled')
        } else {
            let flightInfo = await response.json()
            console.log(flightInfo)

            let chosenFlightHeader = document.getElementById('chosen-flight-header')
            let chosenFlightImage = document.getElementById('chosen-flight-image')

            let fromCode = document.getElementById('from-header')
            let toCode = document.getElementById('to-header')
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

            let airlineCode = flightCode.substring(0, 2)
            let mainFlightInfo = flightInfo['FlightInformation']['Flights']['Flight']

            // HEADER AND FLIGHT CARRIER INFO
            chosenFlightHeader.textContent = flightCode
            chosenFlightImage.src = codeImageDict[airlineCode]
            fromCode.textContent = mainFlightInfo['Departure']['AirportCode']
            toCode.textContent = mainFlightInfo['Arrival']['AirportCode']

            // TERMINAL INFO
            let terminalInfoD = mainFlightInfo['Departure']['Terminal']
            if (terminalInfoD.hasOwnProperty('Name') && terminalInfoD.hasOwnProperty('Gate')) {
                fromTerm.textContent = `TERMINAL ${terminalInfoD['Name']} - GATE ${terminalInfoD['Gate']}`
            } else if (terminalInfoD.hasOwnProperty('Name')) {
                fromTerm.textContent = `TERMINAL ${terminalInfoD['Name']}`
            } else if (terminalInfoD.hasOwnProperty('Gate')) {
                fromTerm.textContent = `GATE ${terminalInfoD['Gate']}`
            } else {
                fromTerm.textContent = 'TERMINAL'
            }

            // TERMINAL INFO
            let terminalInfoA = mainFlightInfo['Arrival']['Terminal']
            if (terminalInfoA.hasOwnProperty('Name') && terminalInfoA.hasOwnProperty('Gate')) {
                toTerm.textContent = `TERMINAL ${terminalInfoA['Name']} - GATE ${terminalInfoA['Gate']}`
            } else if (terminalInfoA.hasOwnProperty('Name')) {
                toTerm.textContent = `TERMINAL ${terminalInfoA['Name']}`
            } else if (terminalInfoA.hasOwnProperty('Gate')) {
                toTerm.textContent = `GATE ${terminalInfoA['Gate']}`
            } else {
                toTerm.textContent = 'TERMINAL'
            }

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

            if (mainFlightInfo['Status']['Code'] === 'LD') {
                let secTaken = (actualArrival.getTime() - actualDeparture.getTime()) / 1000
                let minTaken = (secTaken / 60) % 60
                let hoursTaken = secTaken / 3600 
                console.log(secTaken / 60)
                console.log(secTaken / 3600)

                console.log(minTaken)
                console.log(hoursTaken)

                progressBar.value = "100"
                flightTime.textContent = `${Math.floor(hoursTaken)} HOURS, ${Math.floor(minTaken)} MINUTES`
                flightRemaining.textContent = `0 HOURS 0 MINUTES`
            }
        }

    } catch (error) {
        console.error(error);
    }

}

async function updateFlightBox() {
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
                        prevDate.setDate(prevDate.getDate() - 2)

                        const isoFormatter = new Intl.DateTimeFormat('en-CA', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                        })

                        fetchFlightStatus(cleanedFlightCode, flightCodeBox, isoFormatter.format(prevDate))
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


let sidebarButton = document.querySelector('#sidebar-button')
let sidebar = document.querySelector('.sidebar');
let buttonIcon = document.querySelector('#sidebar-btn-img');

console.log(sidebarButton)
console.log(sidebar)
console.log(buttonIcon)

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

updateFlightBox()








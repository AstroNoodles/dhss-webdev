// Michael Batavia - JS Code for Flight API Query

async function updateFlightBox() {
    let flightBox = document.querySelector(".codelist")
    const flightsURL = 'https://raw.githubusercontent.com/AstroNoodles/dhss-webdev/refs/heads/main/visual-collection/interesting_flights.txt'
    try {
        const response = await fetch(flightsURL)
        if(!response.ok) {
            throw new Error(`Response status: ${response.status}, ${response.statusText}`);
        } else {
            // do stuff
            let flights = await response.text()
            console.log(flights)
            let cleanedFlightsArr = flights.split("/n")
            console.log(cleanedFlightsArr)
            cleanedFlightsArr.forEach((flightCode) => {
                let cleanedFlightCode = flightCode.substring(0, 5)
                console.log(cleanedFlightCode)

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
    if(prevDisplayStyle === 'none') {
        sidebar.style.display = 'block';
        buttonIcon.src = 'double-arrow-down.png'
    } else {
        sidebar.style.display = 'none';
        buttonIcon.src = 'double-arrow-right.png'
    }
})

updateFlightBox()








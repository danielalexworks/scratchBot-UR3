host = "192.168.1.59"

function getSettingsData(){
    fetch('/api/get_settings_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: 'all' }),
    })
    .then(response => response.json())
    .then(data => {
        fillSettings(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateSettings(data = false){
    var payload = {};

    if (!data){
         payload = JSON.stringify(getEditedSettings())
    }else{
        payload['filterIds'] =  data.join(',');
        payload = JSON.stringify(payload);
    }
    console.log(payload);
    fetch('/api/update_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body:payload,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        getSettingsData()
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function manualAction(action, value = false, direction = false){
   
    data = {}
    data['action'] = action;
    if( value ) data['value'] = value;
    if( direction ) data['direction'] = direction;
    console.log(data);

    fetch('/api/manual_actions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function programAction(action){
   
    data = {}
    data['action'] = action;

    fetch('/api/program_actions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        getSettingsData()
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function getTicket(){
   
    console.log('getticket');
    fetch('/api/get_ticket', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
       
    })
    .then(response => response.json())
    .then(data => {
        
        displayTicket(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function scratchedStatus(){
   
    console.log('scratchStatus');
    fetch('/api/scratch_status', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
       
    })
    .then(response => response.json())
    .then(data => {
        //getSettingsData()
        updatedTicket(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

/*

$('#test').click(function(){
    fetch('http://127.0.0.1:8000/api/call_function', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: 'Hello from HTML!' }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response: ' + data.result);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
})

*/
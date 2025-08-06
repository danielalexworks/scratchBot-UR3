host = "192.168.1.59"
pythonhost = "192.168.1.9"
pythonhost ="127.0.0.1"
pythonhost = (window.location.host).split(':')[0];
console.log(pythonhost);
var wsRunning = false;
var socket;
 function startWS(){
    socket = new WebSocket('ws://'+ pythonhost + ':8765');

    socket.onmessage = function(event) {
        data = JSON.parse(event.data);
        //console.log("DATA LINES: ");
        //console.log(data['lines'])
        //console.log('Message from server:', event.data);
        scratched = data['scratched'];
        //console.log(scratched);
        if(scratched != 'ready'){
           // console.log('scratched update')
            updatedTicket(scratched);
        }

        drawLines(data['lines']);

        // You can trigger DOM changes or other actions here
    };
    socket.onopen = function() {
        //console.log('WebSocket connection established');
        wsRunning = true;

    };
 }


function getSettingsData(){
    fetch('/api/get_settings_data', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        //body: JSON.stringify({ data: 'all' }),
    })
    .then(response => response.json())
    .then(data => {
        fillSettings(data);
        getTicket();
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

function adjustTCP(action, value = false, direction = false){
    data = {}
    data['action'] = action;
    if( value ) data['value'] = value;
    if( direction ) data['direction'] = direction;
    console.log(data);

    fetch('/api/adjust_TCP', {
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


function manualRotate(action, value = false, direction = false){
    data = {}
    data['action'] = action;
    if( value ) data['value'] = value;
    if( direction ) data['direction'] = direction;
    console.log(data);

    fetch('/api/manual_rotate', {
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

        if(action != 'nextgroup')
            getSettingsData()

        if( action == 'start' && settings['status']['value'] != 'paused'){
            startWS();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function alignTicket(pl){
   
    data = {}
    data['location'] = pl;

    fetch('/api/align_ticket', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)

        console.log("READY TO ALIGN TICKET")
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function enableFreeDrive(){
   
    fetch('/api/enable_free_drive', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)

        
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
        console.log(data);
        displayTicket(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function estimateTime(){
    console.log('et)');
    $('#overlay').removeClass('hideit');
    fetch('/api/estimate_time', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
       
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert("Program will take an estimated:\r\n" + data['result'] + " minutes +/-20% or so");
        $('#overlay').addClass('hideit');
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


//TODO move to front end helpers
function scratchedStatus(){
   

   if(!wsRunning){
            startWS();
        }

        /*
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
        updatedTicket(data['result'])
        if(!wsRunning){
            startWS();
        }
        //drawLines(data['lines'])
        
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    */
}

function goToPose(pose){
    data = {}
    data['pose'] = pose;

    fetch('/api/go_to_pose', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('--------MOVED TO ' + pose)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function setNewStartingPose(action){

    $('#overlay').removeClass('hideit');
        var counter = 30
        let inter = setInterval(() =>{
            counter--;
            if(counter <0){
                $('#overlay').addClass('hideit');
                clearInterval(inter);
            }else{
                $('#seconds').html(counter);
            }
        },1000)


    fetch('/api/set_new_starting_pose', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log("DATA " + data)
        //start pose timer
        




    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function shutdown(){
    
    fetch('/api/shutdown', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('-------- SHUTDOWN');
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function goToBox(box){
    
    data = {};
    data['box'] = box;

    fetch('/api/go_to_box', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('--------MOVED TO ' + box)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function scratchABox(box){
    data = {};
    data['box'] = box;

    fetch('/api/scratch_single_box', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('--------SCRATCHED BOX #' + box)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function sendCamTo(loc){
    console.log("MOVING TO " + loc);
    data = {};
    data['loc'] = loc
    fetch("/api/send_cam_to", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('--------MOVED TO ' + loc)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateArduinoCamSettings(){
    data = {}
    fetch("/api/update_arduino_cam_settings", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('cam position found')
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
function figureCamPosition(){
    data = {}
    fetch("/api/figure_cam_position", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log('cam position found')
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
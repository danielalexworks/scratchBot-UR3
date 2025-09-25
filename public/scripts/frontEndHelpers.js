

var boxMode = false;
var singleScratchMode = false;
var settings = {}
var filterIds = [];
var ticketH = 0;
var ticketW = 0;

var settingHR = {
	"scratchData" : 				"Ticket Scratch Data",
	"scratchOrder": 				"Scratch Program",
	"alignoffx" : 					"Aligner Offset X",
	"alignoffy" : 					"Aligner Offset Y",
	"zStartOffset": 				"Aligner Offset Z",
	"adjustx":  						"X Ajustment for Ticket Varation",
	"adjusty":  						"Y Ajustment for Ticket Varation",
	"acceleration":   			"Acceleration for Regular Movement (0-1)", 
	"velocity":       			"Velocity for Regular Movement (0-1)",
	"scratchAcceleration":  "Acceleration for Scratching Movement (0-1)", 
	"scratchVelocity":      "Velocity for Scratching Movement (0-1)",
	"forceScratch": 				"Target Force for Scratching",
	"forceWiggleRoom": 			"+/- Allowed Deviation from Force Target",
	"bitw": 								"Width of Bit (scratch path width)",
	"filterIds": 						"Box Ids to be Scratched in Next Filtered Group (csv)",
	"poses" : 							"Move To Stored Pose",
	"bugp":  								"Verbose Logging",
	"poweredTool":  				"Tool Power",
	"checkForce":  					"Use Force Adjustments in Scratching",
	"adjustmentMulti": 			"Force Adjustment Multiplier 	(~2)"

};

function fillSettings(data){
	settings = data['result'];
	data = data['result'];

	if(filterIds.length >0)
			filterIds = data['filterIds']['value'].split(',');
	$('#settings').html('');

	for( const k in data){
	
			if(data.hasOwnProperty(k)){
				const t = data[k]['type'];
				const v = data[k]['value'];
				
				if (k != 'status' && t != 'info'){
					str = ''
					str += '<tr><td class="settingLabel">';
					if( k in settingHR ) str += settingHR[k];
					else str += k; 
					str += '</td>';
					str += '<td>';
					if(['float', 'int', 'string'].includes(t)){
						str += '<input id="' + k + '" type="text" value="' + v + '" />'
					}else if(t == 'bool'){

						str += '<label>T</label><input type="radio" name="' + k + '" id="' + k + '1" value="1" ';
						if(v == true) str += 'checked';
						str += ' />';

						str += '<label>F</label><input type="radio" name="' + k + '" id="' + k + '2" value="0" ';
						if(v == false) str += 'checked';
						str += ' />';
					}else if(t =='file'){
						str += '<input type="file" id="' + k + '" value="' + v + '" />current:<labe>' + v + '</label>';
					}else if(t == 'select'){
						str += '<select id="' + k + '">';
						data[k]['options'].forEach(o=>{
							str += '<option value="' + o + '"';
							if( v == o) str += ' selected ';
							str += '>' + o + '</option>'
						});
						str += '</select>';
					}else if (t == 'buttons'){
						
						if(v.length > 0){
							
							for (let p of v){
								str += '<button class="poseButton" type="button" id="' + p + '">' + p + '</button>';
							}
							
						}
					}
					str += '</td></tr>';
					$('#settings').append(str)
					//$('#' + k).val(data[k]);
					activatePoseButtons();
				}

				
			}else{
				//console.log('no ' + k)
			}
	}	

	$('#ticket').html(data['scratchData']['value'].split('_')[0]);
	$('#program').html(data['scratchOrder']['value']);
	$('#status').html(data['status']['value']);

}

function activatePoseButtons(){
	
	$('.poseButton').off().click(function(){
			//console.log($(this).attr('id'));
			goToPose($(this).attr('id'));
	})
}

//[-70, -9, 20, 13, "top row", "3", 1, 1, 1]

var ticket = [];
var scratchInt;
function displayTicket(data){
	//console.log(data)
	//const rowNames = [...new Set(array.map(item => item[4]))];
	ticket = JSON.parse(data['result']);
	ticket_info = ticket['ticket_info'];
	ticket = ticket['boxes'];

	updateTicketInfo(ticket_info);
	//console.log(filterIds);

	str = '';
	ticket.forEach((b) => {
		//console.log("box:" + b);
		var t = (b[1])*3 //- b[3]*3 // - settings['offy']['value']);
		var l = (b[0])*3 //- settings['offx']['value']);
		//console.log(t + ' ' +b[1])
		//console.log(l + ' ' +b[0])
		str += "<div id='t" + b[8] + "'";
		str += " style='top:" + t + "px;";
		str += " left:" + l + "px;";
		str += " width:" + b[2]*3 + "px;";
		str += " height:" + b[3]*3 + "px;'";
		str += "><button id = 'b" + b[8] + "' type='button'";
		//console.log(b[8]);
		if(filterIds.includes(b[8].toString())){
		 	str += " class = 'filters'"
		 //	console.log("++++++++++++++++++++++++++++++++++"+b[8]);
		}
		str +=">" + b[8] + "</button></div>"
	});

	$('#ticket_interface').html(str);
	if(typeof scratchInt !== 'undefined') clearInterval(scratchInt);
	scratchInt = setInterval(()=>{
		scratchedStatus();
		
	},5000)

	activateTicketButtons();

}

function updateTicketInfo(ticket){
	$('#ticket').html(ticket['ticket_name']);

	ticketH = parseInt(ticket['ticket_height']);
	ticketW = parseInt(ticket['ticket_width']);

	$('#ticketdrawing').attr('width', parseInt(ticket['ticket_width']) *3);
	$('#ticketdrawing').attr('height', parseInt(ticket['ticket_height']) *3);
	$('#ticketdrawing').css('width',  parseInt(ticket['ticket_width']) *3);
	$('#ticketdrawing').css('height',  parseInt(ticket['ticket_height']) *3);

	$('#drawing').attr('width', parseInt(ticket['ticket_width']) *3);
	$('#drawing').attr('height', parseInt(ticket['ticket_height']) *3);
	$('#drawing').css('width',  parseInt(ticket['ticket_width']) *3);
	$('#drawing').css('height',  parseInt(ticket['ticket_height']) *3);

	$('#ticket_interface').attr('width', parseInt(ticket['ticket_width']) *3);
	$('#ticket_interface').attr('height', parseInt(ticket['ticket_height']) *3);
	$('#ticket_interface').css('width',  parseInt(ticket['ticket_width']) *3);
	$('#ticket_interface').css('height',  parseInt(ticket['ticket_height']) *3);

}

function updatedTicket(scratched){
	console.log(scratched);
	
	if(scratched){
			if(scratched == 'ready'){
					$('#status').html('ready');
			}else{
				//console.log(scratched)
				$('#ticket_interface div button').addClass('scratched');

				//notscratched
				scratched.forEach((s) => {
					$('#t' + (s) + ' button').removeClass('scratched');
				});

				$('#ticket_interface div button').each(function(){
					if ($(this).hasClass('scratched')){
						$(this).removeClass('filters');
					}
				});
			}
	}
	//console.log("FID " + filterIds);

}

//var drawnLines = []
function drawLines(lines){
		var c = 0;
		
		if(lines){	
			context.clearRect(0, 0, canvas.width, canvas.height);
			context.moveTo(0,0);
			for (let l of lines){
			
				//draw center of bit line
				drawLine(c, l, 'green');

			}
		}
}

function drawLine(c, l, color = 'lightblue'){
		context.strokeStyle = color;
	 	context.beginPath();
	 	//console.log("L : " + l)
	 	/*
	 	fx = (l[0] - settings['offx']['value']) *3
	 	fy = (l[1] - settings['offy']['value']) *3
	 	tx = (l[2] - settings['offx']['value']) *3
	 	ty = (l[3] - settings['offy']['value']) *3

	 	fx = (-settings['offx']['value'] + l[0]) *3
	 	fy = (-settings['offy']['value'] + l[1]) *3
	 	tx = (-settings['offx']['value'] + l[2]) *3
	 	ty = (-settings['offy']['value'] + l[3]) *3
	 	*/

	 	fx = ( l[0]) *3
	 	fy = ( l[1]) *3
	 	tx = ( l[2]) *3
	 	ty = ( l[3]) *3

	 	//console.log(fx + "," +fy + " -> " + tx +"," +ty)
  	context.moveTo(fx,fy); // Starting point (x, y)
  	context.lineTo(tx,ty); // Ending point (x, y)
  	context.stroke(); // Render the line


}

function arraysEqual(arr1, arr2) {
  return JSON.stringify(arr1) === JSON.stringify(arr2);
}

var filterIds = [];
function activateTicketButtons(){
	//console.log(ticket);
	$('#ticket_interface button').click(function(){

			var boxId = $(this).attr('id').slice(1);
			var box = ticket[boxId -1];

			if(!boxMode && !singleScratchMode){
				if( !$(this).hasClass('scratched') && box[5].includes('f') ){
					if(filterIds.includes(boxId)){
							filterIds = filterIds.filter(item => item !== boxId);
					}else{
							filterIds.push(boxId);
						}
					$(this).toggleClass('filters');
					filterIds = filterIds.filter(value => value !== '');
					console.log(filterIds);
					updateSettings(filterIds);
				}
			}else if(boxMode){
				boxModeGoto(boxId);
			}else if(singleScratchMode){
				scratchSingleBox(boxId);
			}
			

	});
}



function getEditedSettings(){
	s = {}

    for( const k in settings ){

        if(settings[k]['type'] == 'bool'){
        	if(settings[k]['value'] != $('input[name=' + k + ']:checked').val()){	
        		s[k] = parseInt($('input[name=' + k + ']:checked').val());// ? true : false;
       		}
        }else if(settings[k]['type'] == 'select'){
          if(settings[k]['value'] != $('#' + k + ' option:selected').val()){
        	
        		s[k] = $('#' + k + ' option:selected').val();
        	}

        }else if(['int','float','string'].includes(settings[k]['type'])){
        	if( settings[k]['value'] != $('#' + k).val() ){       	        	
	          s[k] = $('#' + k).val();
        	}
        }
    }

   return s
}

var canvas;
var context;

$(document).ready(function(){ 
		getSettingsData();

		canvas = document.getElementById('ticketdrawing');
		context = canvas.getContext('2d');
		canvas.style.backgroundColor = 'black';
		
		//manual section buttons
		$('.manual').click(function(){
			//JOGS
			if($(this).hasClass('jog')){
					var a = $(this).attr('id').charAt(0);
					var d = $(this).attr('id').slice(1);
					var v = $(this).siblings('input[type="text"]').val();
					manualAction(a,v,d);
			}else if($(this).hasClass('rot')){
				var a = $(this).attr('id').charAt(0);
				var d = $(this).attr('id').slice(2);
				var v = $(this).siblings('input[type="text"]').val();
				manualRotate(a,v,d);

			}else if($(this).hasClass('adjust')){
				var a = $(this).attr('id').charAt(0);
				var d = $(this).attr('id').slice(2);
				var v = $(this).siblings('input[type="text"]').val();
				adjustTCP(a,v,d);
			}else{
				var a = $(this).attr('id');
				manualAction(a)
			}
		});

		$('.program').click(function(){
			programAction($(this).attr('id'));
		});


		$('#shutdown').click(function(){
			shutdown();
		})

		$('#setNewStartingPose').click(function(){
			setNewStartingPose();
		})

		$('#boxToggle').click(function(){
			toggleBoxMode();
		})

		$('#singleScratchToggle').click(function(){
			singleScratchModeToggle();
		})

		$('#freeDrive').click(function(){
			enableFreeDrive();
		})

		$('#alignTicket').click(function(){
			alignTicketClick();
		})

		$('#estimate').click(function(){
			estimateTime();
		})

		$('.cam').click(function(){
			n = $('.' + $(this).attr('id'));
			if(n.length)
				n = $('.' + $(this).attr('id')).val();
			else
				n = false

			console.log(n);
			camFun($(this).attr('id'),n);
		})
})

function camFun(id, n){
	if(id == 'camToFront'){
		sendCamTo('front');
	}else if(id == 'camToBack'){
		sendCamTo('back');
	}else if(id == 'camToTicketTop'){
		sendCamTo('ticketTop');
	}else if(id == 'camToMm'){
		sendCamTo(n);
	}else if(id == 'figurePosition'){
		figureCamPosition()
	}else if(id == 'camUpdate'){
		fetch("../poseData/camSettings.json")
		  .then(response => response.json())
		  .then(data => {
		    let obj = data;
		    console.log(obj);
		  });
		//updateArduinoCamSettings()
	}

}

function toggleBoxMode(){
	boxMode = !boxMode;
	scratchSingleBox();
	if(boxMode && singleScratchMode) singleScratchModeToggle();
	if(boxMode){
		$('#ticket_interface div button').addClass('boxMode');
	}else{
		$('#ticket_interface div button').removeClass('boxMode');
	}
}

function boxModeGoto(box = false){
	
	if(box){
		$('#ticket_interface div button').removeClass('boxModeActive');
		$('#ticket_interface div button').addClass('boxMode');
		$('#ticket_interface div button#b' + box).removeClass('boxMode');
		$('#ticket_interface div button#b' + box).addClass('boxModeActive');
		goToBox(box); 
	}else{
		$('#ticket_interface div button').removeClass('boxModeActive');
		$('#ticket_interface div button').removeClass('boxMode');
	}
}

function singleScratchModeToggle(){
	singleScratchMode = !singleScratchMode;
	boxModeGoto()
	if(boxMode && singleScratchMode) toggleBoxMode();
	if(singleScratchMode){
		$('#ticket_interface div button').addClass('singleScratchMode');
	}else{
		$('#ticket_interface div button').removeClass('singleScratchMode');
	}
}

function scratchSingleBox(box = false){
	
	if(box){
		$('#ticket_interface div button').removeClass('singleScratchModeActive');
		$('#ticket_interface div button').addClass('singleScratchMode');
		$('#ticket_interface div button#b' + box).removeClass('singleScratchMode');
		$('#ticket_interface div button#b' + box).addClass('singleScratchModeActive');
	
		if(confirm("Are you sure that you want to scratch box #"+ box + "?\r\n\r\nBOX #" + box + " will be scratched immediately, if confirmed.")){
			scratchABox(box);
		}else{
			$('#ticket_interface div button').removeClass('singleScratchModeActive');
			$('#ticket_interface div button').removeClass('singleScratchMode');
		}
	}else{
		$('#ticket_interface div button').removeClass('singleScratchModeActive');
		$('#ticket_interface div button').removeClass('singleScratchMode');
	}
}

var corner = 'top left'
function alignTicketClick(){
	var pl;
	if(corner == 'top left'){
		pl = 'tl';
		corner = 'bottom left';
	}else{
		pl = 'bl';
		corner = 'top left';
	}

	alignTicket(pl);

}
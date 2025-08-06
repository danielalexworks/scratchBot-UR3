


var settings = {}
function fillSettings(data){
	settings = data
	data = data['result']
	console.log(data);
	$('#settings').html('');

	for( const k in data){
	
			if(data.hasOwnProperty(k)){
				const t = data[k]['type'];
				const v = data[k]['value'];
				console.log(t);
					if (k != 'status'){
					str = ''
					str += '<tr><td>' + k + '</td>';
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
					}
					str += '</td></tr>';
					$('#settings').append(str)
					//$('#' + k).val(data[k]);
				}
				
			}else{
				console.log('no ' + k)
			}
	}	

	$('#ticket').html(data['scratchData']['value'].split('_')[0]);
	$('#program').html(data['scratchOrder']['value']);
	$('#status').html(data['status']['value']);

}


//[-70, -9, 20, 13, "top row", "3", 1, 1, 1]

var ticket = [];
function displayTicket(data){
	console.log(data)
	//const rowNames = [...new Set(array.map(item => item[4]))];
	data = JSON.parse(data['result']);
	ticket = data;

	str = '';
	data.forEach((b) => {
		str += "<div id='t" + b[8] + "'";
		str += " style='top:" + Math.abs(b[1])*3 + "px;";
		str += " left:" + Math.abs(b[0])*3 + "px;";
		str += " width:" + b[2]*3 + "px;";
		str += " height:" + b[3]*3 + "px;";
		str += "'><button id = 'b" + b[8] + "' type='button'>" + b[8] + "</button></div>"
	});

	$('#ticket_interface').html(str);
	setInterval(()=>{
		scratchedStatus();
		
	},5000)

	activateTicketButtons();

}

function updatedTicket(scratched){
	scratched = scratched['result']
	if(scratched){
			if(scratched == 'ready'){
					$('#status').html('ready');
			}else{
				console.log(scratched)
				$('#ticket_interface div button').addClass('scratched');

				scratched.forEach((s) => {
					$('#t' + s + ' button').removeClass('scratched');
				});

				$('#ticket_interface div button').each(function(){
					if ($(this).hasClass('scratched')){
						$(this).removeClass('filters');
					}
				});
			}
	}
	console.log(filterIds);
}

var filterIds = [];
function activateTicketButtons(){
	$('#ticket_interface button').click(function(){
			var boxId = $(this).attr('id').slice(1);
			var box = ticket[boxId -1];
			if( !$(this).hasClass('scratched') && box[5].includes('f') ){
				if(filterIds.includes(boxId)){
						filterIds = filterIds.filter(item => item !== boxId);
				}else{
						filterIds.push(boxId);
					}
				$(this).toggleClass('filters');
				updateSettings(filterIds);
			}
			

	});
}

function getEditedSettings(){
	s = {}
	settings = settings['result'];

    for( const k in settings ){

        if(settings[k]['type'] == 'bool'){
        	if(settings[k]['value'] != $('input[name=' + k + ']:checked').val()){	
        		s[k] = $('input[name=' + k + ']:checked').val() ? false : true;
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


$(document).ready(function(){
		
		//manual section buttons
		$('.manual').click(function(){
			//JOGS
			if($(this).hasClass('jog')){
					var a = $(this).attr('id').charAt(0);
					var d = $(this).attr('id').slice(1);
					var v = $(this).siblings('input[type="text"]').val()
					manualAction(a,v,d);

			}else{
				var a = $(this).attr('id');
				manualAction(a)
			
			}
		});


		$('.program').click(function(){
			programAction($(this).attr('id'));
		});

		getTicket()






})

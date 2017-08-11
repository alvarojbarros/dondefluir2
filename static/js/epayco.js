function getQueryParam(param) {
    location.search.substr(1)
        .split("&")
        .some(function(item) { // returns first occurence and stops
            return item.split("=")[0] == param && (param = item.split("=")[1])
        })
    return param
}


function processPayment(activityId){
    //llave publica del comercio

    //Referencia de payco que viene por url
    var ref_payco = getQueryParam('ref_payco');
    //Url Rest Metodo get, se pasa la llave y la ref_payco como paremetro
    var urlapp = "https://api.secure.payco.co/validation/v1/reference/" + ref_payco;

    $.get(urlapp, function(response) {


        if (response.success) {

            if (response.data.x_cod_response == 1) {
                //Codigo personalizado
                //alert("Transaccion Aprobada");
                console.log('transacción aceptada');
            }
            //Transaccion Rechazada
            if (response.data.x_cod_response == 2) {
                console.log('transacción rechazada');
            }
            //Transaccion Pendiente
            if (response.data.x_cod_response == 3) {
                console.log('transacción pendiente');
            }
            //Transaccion Fallida
            if (response.data.x_cod_response == 4) {
                console.log('transacción fallida');
            }

            $('#fecha').html(response.data.x_transaction_date);
            $('#respuesta').html(response.data.x_response);
            $('#referencia').text(response.data.x_id_invoice);
            $('#motivo').text(response.data.x_response_reason_text);
            $('#recibo').text(response.data.x_transaction_id);
            $('#banco').text(response.data.x_bank_name);
            $('#autorizacion').text(response.data.x_approval_code);
            $('#total').text(response.data.x_amount + ' ' + response.data.x_currency_code);

			vars = {activityId: activityId}
			KeyNames = Object.keys(response.data);
			for (key in KeyNames){
				vars[KeyNames[key]] = response.data[KeyNames[key]];
			}
			$.getJSON($SCRIPT_ROOT + '/_set_payment',vars, function(data) {
				if (data.result['res']==true){
					history.pushState(null, null, '/#');
				}
			});

        } else {
            //alert("Error consultando la información");
        }
    });
}

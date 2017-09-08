/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction(n) {
    document.getElementById("myDropdown"+n).classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function refreshList() {
	$('#searchDiv').load(document.URL +  ' #searchDiv');
	//setTimeout(arguments.callee, 3000);
}


function newRecord(Table,TemplateName) {
    if (!TemplateName){
        TemplateName = 'recordform.html';
    }
    var vars = {Template: TemplateName,Table: Table,RecordId: ''}
    getTemplate(vars,function(){
		getRecord({TableName: Table},function (data){
			Vue.set(vue_record,'record', data.record);
			Vue.set(vue_record,'links', data.links);
			Vue.set(vue_record,'table', Table);
			Vue.set(vue_buttons,'canEdit', data.canEdit);
			Vue.set(vue_buttons,'canDelete', data.canDelete);
			setCustomVue(TemplateName,data.record,Table);
			vue_title.Title = 'Nuevo Registro'
		})
	})
}


function sendFiles(table,id){

	var files = new FormData();
	FilesInputs = document.getElementsByClassName('fileinput-filename');
	for (k in FilesInputs){
		e = FilesInputs[k];
		efile = document.getElementById(e.id + '-file');
		if (efile){
			if (efile.files.length>0){
				if (efile.files[0].size>512000){
					alert('El tama&ntilde;o de imagen debe ser de 500 Kb')
					return;
				}
				files.append(e.id + '-table',table);
				files.append(e.id + '-id',id);
				files.append(e.id,efile.files[0]);
			}
		}
	}

	$.ajax({
		type: 'POST',
		url: '/_save_files',
		data: files,
		contentType: false,
		cache: false,
		processData: false,
		success: function(data) {
			//alert("OK");
		},
		failure: function(data){
			alert("No es posible actualizar archivos");
		}
	});
}

function saveRecord(table) {
    fields = vue_record.record;
    fields.TableName = table;
  	var _state = document.getElementById('_state');
    fields._state = _state.value

	$.ajax({
	  type: "POST",
	  url: "/_save_record",
	  data: fields,
	  success: function (data) {
      	res = data.result.res
      	messages.error_msg  = '';
      	if (res){
      		vue_record.record = data.result.record;
      		vue_record._state = 1
      		if (data.result.Name){
				vue_title.recordName = data.result.Name
			}else{
				vue_title.recordName = data.result.id
			}
      		sendFiles(table,data.result.id);
			setMessageTimeout('Registro Grabado')
      		if (data.result.RunJS){
				var callback_function = new Function(data.result.RunJS);
				callback_function();
			}
	  	}else{
			messages.error_msg = data.result.Error;
		};
	  },
	  dataType: "json"
	});

    //$.getJSON($SCRIPT_ROOT + '/_save_record', fields, function(data) {
    //});

};


function getRecordForm(Table,TemplateName,id,callName,runFunction){
	var titleName = vue_title.Title;
    var moduleNr = vue_title.moduleNr;
    var index = vue_title.indexNr ;
	if (runFunction){
		var callback_function = new Function(runFunction);
		callback_function();
	}
    var vars = {Template: TemplateName,Table: Table, id: id}
	if (callName){
		var callback_function = new Function(callName);
		getTemplate(vars,function(){
			callback_function();
			getRecord({TableName: Table,id: id},function (data){
                vue_title.moduleNr = moduleNr;
                vue_title.indexNr = index;
				Vue.set(vue_record,'table', Table);
				Vue.set(vue_title,'tableName', titleName);
				Vue.set(vue_record,'values', data);
				Vue.set(vue_buttons,'canEdit', data.canEdit);
				Vue.set(vue_buttons,'canDelete', data.canDelete);
				setCustomVue(TemplateName,data.record,Table);
				if (data.record['Name']){
					vue_title.recordName = data.record['Name']
				}else{
					vue_title.recordName = data.record['id']
				}
			})
		})
	    //getTemplate(vars,null);
	}else{
	    getTemplate(vars,function (){
			getRecord({TableName: Table,id: id},function (data){
                vue_title.moduleNr = moduleNr;
                vue_title.indexNr = index;
				Vue.set(vue_record,'table', Table);
				Vue.set(vue_title,'tableName', titleName);
				Vue.set(vue_record,'values', data);
				Vue.set(vue_buttons,'canEdit', data.canEdit);
				Vue.set(vue_buttons,'canDelete', data.canDelete);
				setCustomVue(TemplateName,data.record,Table);
				if (data.record['Name']){
					vue_title.recordName = data.record['Name']
				}else{
					vue_title.recordName = data.record['id']
				}
			})
		});
	}
}



function getRecord(filters,callbalck,values) {
    console.log(filters);
    socket.emit('_get_record', filters, values, function (data) {
        console.log(data.result);
        if (data.result.record.id){
            data.result['_state'] = 1
        }else{
            data.result['_state'] = 0
        }
        callbalck(data.result)
    });
    return;
}


/*function getRecord(filters,callbalck,values){
  $.getJSON($SCRIPT_ROOT + '/_get_record', {Filters: filters,Values: values}, function(data) {
    if (data.result.record.id){
    	data.result['_state'] = 1
	}else{
    	data.result['_state'] = 0
	}
    callbalck(data.result)
  });

}*/

function getRecordBy(Table,filters,callbalck){
  filters.TableName = Table;
  /*$.getJSON($SCRIPT_ROOT + '/_get_record', filters, function(data) {
    callbalck(data.result)
  });*/

    console.log(filters)
    socket.emit('_get_record',filters,{}, function (data) {
        console.log(data.result);
        callbalck(data.result)
    });

}


function deleteRecord(table) {
    var fields = {}
    fields['TableName'] = table;
    messages.error_msg = '';
	_id = vue_record.values.record.id;
    if (_id){
		fields['id'] = _id;
		$.getJSON($SCRIPT_ROOT + '/_delete_record', fields, function(data) {
		  if (data.result['res']){
			  setMessageTimeout('Registro Borrado')
		  }else{
			  messages.error_msg = data.result['Error'];
		  }
		});
	}else{
	  alret('Registro No grabado. No se puede eliminar')
	}
};


function sortDict(obj){
	return Object.keys(obj).sort()
}

function findComponent(id){
    var components = [];
    for (k in vue_recordlist.$children){
        component = vue_recordlist.$children[k];
        if (component.record.id==id){
            components.push(component);
        }
    }
    return components;
}

var normalize = (function() {
  var from = "ÃÀÁÄÂÈÉËÊÌÍÏÎÒÓÖÔÙÚÜÛãàáäâèéëêìíïîòóöôùúüûÑñÇç",
      to   = "AAAAAEEEEIIIIOOOOUUUUaaaaaeeeeiiiioooouuuunncc",
      mapping = {};

  for(var i = 0, j = from.length; i < j; i++ )
      mapping[ from.charAt( i ) ] = to.charAt( i );

  return function( str ) {
      var ret = [];
      for( var i = 0, j = str.length; i < j; i++ ) {
          var c = str.charAt( i );
          if( mapping.hasOwnProperty( str.charAt( i ) ) )
              ret.push( mapping[ c ] );
          else
              ret.push( c );
      }
      return ret.join( '' );
  }

})();

function searchBoxOnKey(e){
	var filter = $(e).val().toLowerCase();
    for (r in vue_recordlist.values){
        record = vue_recordlist.values[r]
        components = findComponent(record.id);
        if (components.length>0 && (!vue_recordlist.values[r].text_list)){
            vue_recordlist.values[r].text_list = [];
            for (k in components){
                component = components[k];
                vue_recordlist.values[r].text_list.push(component.text.toLowerCase())
            }
        }
        var found = true;
        words = filter.split(' ');
        for (j = 0; j < words.length; j++) {
            var word = words[j];
            var word_found = false
            if (word){
                word = normalize(word);
                if (components.length>0){
                    for (k in components){
                        component = components[k];
                        a = normalize(component.text.toLowerCase());
                        if (a.indexOf(word)>-1) {
                            word_found = true;
                        }
                    }
                }else{
                    if (vue_recordlist.values[r].text_list){
                        for (k in vue_recordlist.values[r].text_list){
                            text = vue_recordlist.values[r].text_list[k]
                            a = normalize(text);
                            if (a.indexOf(word)>-1) {
                                word_found = true;
                            }
                        }
                    }
                }
                if (!word_found){
                    found = false;
                }
            }

        }
		if (found==true) {
			record._Skip2 = false;
		} else {
			record._Skip2 = true;
		}
    }
}

function runSearchBoxOnKey(){
	$('.list-group-full li').each(function(){
		$(this).attr('data-search-term', $(this).text().toLowerCase());
	});

	$('.live-search-box').on('keyup', function(event){
        searchBoxOnKey(this);
	});
}

jQuery(document).ready(function($){

	getCurrentUser();

	localStorage.clear();
	$('.list-group-full li').each(function(){
		$(this).attr('data-search-term', $(this).text().toLowerCase());
	});

	$('.live-search-box').on('keyup', function(){
		searchBoxOnKey(this);
	});

	getMyFunctionReady();

});


function checkFileSize(e){

	children1 = e.childNodes;
	for (i in children1){
		children2 = children1[i].childNodes;
		for (k in children2){
			childeren3 = children2[k]
			if (childeren3.files){
				oldFile = childeren3.files[0];
				if (childeren3.files[0].size>512000){
					alert('El tama&ntilde;o de imagen debe ser de 500 Kb');
					return;
				}
			}
		}
	}
}

function addNewRow(field){
	fields = vue_record.fields[field];
	new_row = {}
	for (dfield in fields){
		new_row[dfield] = null;
	}
	vue_record.record[field].push(new_row)
}

function removeRow(field,index) {
	vue_record.record[field].splice(index,1);
}


function AddToLocalStorage(html){

	var myIndex = localStorage['index'];
	if (myIndex){
		localStorage['index'] = parseInt(localStorage['index']) + 1;
	}else{
		localStorage['index'] = 1;
	}
	divIndex = 'index' + localStorage['index'];
	localStorage[divIndex] = html;


	/*var i = parseInt(localStorage['index']) + 1;
	var l = localStorage.length;
	for (i; i < localStorage.length; i++) {
		divIndex = 'index' + i;
		localStorage.removeItem(divIndex);
	}*/

}


function getTemplate(vars,callback){
	AddToLocalStorage($('.container-fluid').html())
	var myNode = document.getElementById('container-fluid');
	history.pushState("1","","");

	while (myNode.firstChild) {
		myNode.removeChild(myNode.firstChild);
	}

	runFunction = vars['runFunction'];
	if (runFunction){
		var callback_function = new Function(runFunction);
		callback_function();
	}

  	$.getJSON($SCRIPT_ROOT + '/_get_template', vars ,function(data) {
		var myNode = document.getElementById('container-fluid');
		$(myNode).html(data.result.html)
		functions = data.result.functions;
		if (functions){
			var callback_function = new Function(functions);
			callback_function();
		}
		if (callback){
			callback();
		}
    });
}

function backLocalStorage(){
	divIndex = 'index' + localStorage['index'];
	var myNode = $('.container-fluid');
	myNode.html(localStorage[divIndex])
	localStorage.removeItem(divIndex);
	localStorage['index'] = parseInt(localStorage['index']) - 1;

}

window.onpopstate = function (event) {

	if(event.state) {
		backLocalStorage();
	}
}

function OpenCloseMenu(){
	if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
		$(".navbar-toggle i").toggleClass("ti-menu"),$(".navbar-toggle i").addClass("ti-close")
		e = $(".sidebar-nav").toggleClass("in");
	}
}

function recoverPassword(){
	var e = document.getElementById('Email');
	if (!e.value){
		alert('Debe ingresar Email');
		return;
	}
	messages.error_msg  = '';
  	$.getJSON($SCRIPT_ROOT + '/_recover_password', {'email': e.value},function(data) {
      	res = data.result['res']
      	if (res){
			alert('Se ha enviado un correo con su nuevo password');
			show_signIn();
	  	}else{
			alert(data.result['Error']);
		};
    });
}


function cleanMessageText(text){
	messages.success_msg = '';
}


function setMessageTimeout(text){
	messages.success_msg = text;
	setTimeout("cleanMessageText()", 5000);
}


function changePassword(){
	event.preventDefault()
	var p = document.getElementById('password');
	var p1 = document.getElementById('password1');
	var p2 = document.getElementById('password2');
	messages.error_msg  = '';
	if (p1.value==p2.value){
		$.getJSON($SCRIPT_ROOT + '/_change_password', {'pwd': p.value,'newpwd': p1.value},function(data) {
			res = data.result['res']
			if (res){
				//alert('Se ha modificado el password correctamente');
				setMessageTimeout('Se ha modificado el password correctamente')
			}else{
				//alert(data.result['Error']);
				messages.error_msg = data.result['Error'];
			};
		});
	}else{
		messages.error_msg = "Los password no coinciden";
		return;
	}
}


function getCurrentUser(callback){

  var usermenu = document.getElementById('user-menu');
  if (usermenu){
	$.getJSON($SCRIPT_ROOT + '/_get_current_user_type', {},function(data) {
		Vue.set(vue_user_menu,'current_user_type', data.result.user_type);
		Vue.set(vue_user_menu,'current_user_id', data.result.user_id);
		if (callback){
			callback();
		}
	});
  }
}

function getRecordList(table,fields,limit,order_by,desc){
	var vars = {'Table': table,'Fields': fields }
	if (limit) {vars['Limit'] = limit;}
	if (order_by) {vars['OrderBy'] = order_by;}
	if (desc) {vars['Desc'] = desc;}
	Vue.set(vue_recordlist,'table', table);
	Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	Vue.set(vue_recordlist,'user_id', vue_user_menu.current_user_id);
	$.getJSON($SCRIPT_ROOT + '/_record_list', vars ,function(data) {
		Vue.set(vue_recordlist,'values', data.result.records);
		vue_recordlist.values =  data.result.records;
		Vue.set(vue_recordlist,'filters', data.result.filters);
		Vue.set(vue_recordlist,'filtersNames', data.result.filtersNames);
	});
}


function updateLinkTo(fieldname){
	fields = vue_record.values.record;
	fields['TableName'] = vue_record.table;
	if (fieldname){
		fields['FieldName'] = fieldname;
	}
	$.getJSON($SCRIPT_ROOT + '/_update_linkto', fields,function(data) {
		if (fieldname){
			vue_record.values.links[fieldname] = data.result[fieldname];
		}else{
			vue_record.values.links = data.result;
		}
	});
}

function updateRecordList(div,Filter){
    filters = document.getElementsByName("select-filter")
    for (i in vue_recordlist.values){
        skip = false;
        for (k in filters){
            div = filters[k];
            filter_value = div.value;
            if (filter_value!=div.id){
                if (vue_recordlist.values[i][div.id]!=div.value){
                    skip = true;
                }
            }
        }
        vue_recordlist.values[i]._Skip = skip;
    }
}

function SetReport(ReportClass){
	$.getJSON($SCRIPT_ROOT + '/_get_report', {'Report': ReportClass},function(data) {
	    vue_report.filters = data.result.filters;
	    vue_report.htmlView = data.result.htmlView;
	    vue_report.ReportClass = data.result.ReportClass;
	});
}

function RunReport(){
	report = vue_report.ReportClass;
	vars = {'Report': report}
	for (field in vue_report.filters){
	    vars[field] = vue_report.filters[field].Value;
	}
	$.getJSON($SCRIPT_ROOT + '/_run_report', vars ,function(data) {
	    vue_report_result.Columns = data.result.Columns;
	    vue_report_result.Rows = data.result.Rows;
	});

}

function setTableColumns(columns){
    vue_recordlist.columns = columns;
}

function setVue(data,canEdit,canDelete){
    Vue.set(vue_record,'record', data.record);
    Vue.set(vue_record,'links', data.links);
    Vue.set(vue_record,'fields', data.fields);
    Vue.set(vue_title,'Title', data.record.Name);
    Vue.set(vue_record,'current_user_type', vue_user_menu.current_user_type);
    Vue.set(vue_buttons,'canEdit', canEdit);
    Vue.set(vue_buttons,'canDelete', canDelete);
}

function showProfile(){
	vars = {'Template': 'userform.html','Profile': '1'}
	getTemplate(vars,function(){
        getRecord({TableName: 'User',id: vue_user_menu.current_user_id},function (data){
            setVue(data,true,false);
        })
	});
}

function showUser(user_id){
	vars = {'Template': 'userform.html','Profile': '0'}
	getTemplate(vars,function(){
        getRecord({TableName: 'User',id: user_id},function (data){
            $.getJSON($SCRIPT_ROOT + '/_get_favorite', {'favId': user_id} ,function(data2) {
                setVue(data,data.canEdit,data.canDelete);
                Vue.set(vue_record,'favorite', data2.result);
            });
        });
	});
}

function showCompany(company_id){
	vars = {'Template': 'companyform.html'}
	getTemplate(vars,function(){
        getRecord({TableName: 'Company',id: company_id},function (data){
            setVue(data,data.canEdit,data.canDelete);
        })
	});
}

function showService(id){
	vars = {'Template': 'serviceform.html'}
	getTemplate(vars,function(){
        getRecord({TableName: 'Service',id: id},function (data){
            setVue(data,data.canEdit,data.canDelete);
        })
	});
}

function showUserService(id){
	vars = {'Template': 'userserviceform.html'}
	getTemplate(vars,function(){
        getRecord({TableName: 'UserService',id: id},function (data){
            setVue(data,data.canEdit,data.canDelete);
        })
	});
}

function showActivity(id){
	vars = {'Template': 'activityform.html'}
	getTemplate(vars,function(){
        getRecord({TableName: 'Activity',id: id},function (data){
            setVue(data,data.canEdit,data.canDelete);
            Vue.set(vue_buttons,'id', data.record.id);
            Vue.set(vue_buttons,'Status', data.record.Status);
            Vue.set(vue_activity,'record',data.record)
            if (data.record && data.record.OnlinePayment && data.record.Price){
                Vue.set(vue_activity,'ShowPayment',true);
            }
            if (data.record.OnlinePayment==1){
                $.getJSON($SCRIPT_ROOT + '/_get_payment', {'activityId': data.record.id
                , 'userId': data.record.CustId,'companyId': data.record.CompanyId}
                    , function(data2) {
                    Vue.set(vue_activity,'Paid',data2.result.res)
                    if (!data2.result.res){
                        Vue.set(vue_activity,'KeyPayco',data2.result.KeyPayco)
                    }
                });
            }

        })
	});
}

function showNotification(id,set_read){
	vars = {'Template': 'notificationform.html'}
	getTemplate(vars,function(){
        if (set_read){
            setNotificationRead(id);
        }
        getRecord({TableName: 'Notification',id: id},function (data){
            setVue(data,data.canEdit,data.canDelete);
        })
	});
}

function getActivityColumns(user_type){

    columns = "{0:('Horario','.TransDate de .StartTime a .EndTime')"
    columns += ",1:('Servicio','.ServiceId')"
    columns += ",2:('Estado','.Status')"
    if (user_type==0){
        columns += ",3:('Profesional','.ProfId')"
        columns += ",4:('Cliente','.CustId')";
    }
    if (user_type==1){
        columns += ",3:('Profesional','.ProfId')"
        columns += ",4:('Cliente','.CustId')";
    }
    if (user_type==2){
        columns += ",3:('Cliente','.CustId')";
    }
    if (user_type==3){
        columns += ",3:('Empresa','.CompanyId')"
        columns += ",4:('Profesional','.ProfId')"
    }
    columns += "}";
    return columns;

}

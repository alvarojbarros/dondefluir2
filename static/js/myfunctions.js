
function showProfessional(id,Name,current_user_id){
	var titleName = vue_title.Title;
    var moduleNr = vue_title.moduleNr;
    var index = vue_title.indexNr ;
	vars = {Template: 'showprofessional.html',profId: id}
	getTemplate(vars,function (){
        setProffesional(id,current_user_id);
        vue_title.moduleNr = moduleNr;
        vue_title.indexNr = index;
        vue_title.tableName = titleName;
	})
}

function showCompanyProfile(id,Name){
	var titleName = vue_title.Title;
    var moduleNr = vue_title.moduleNr;
    var index = vue_title.indexNr ;
	vars = {Template: 'showcompany.html',companyId: id}
	getTemplate(vars,function (){
		setCompany(id,vue_user_menu.current_user_id);
        vue_title.moduleNr = moduleNr;
        vue_title.indexNr = index;
		vue_title.tableName = titleName;
	})
}


function getProfessionalList(favorite,current_user_id){
	$.getJSON($SCRIPT_ROOT + '/_get_professional_list', {'favorite': favorite },function(data) {
		Vue.set(vue_recordlist,'values', data.result);
		Vue.set(vue_recordlist,'user_id', current_user_id);
		Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	});
}

function setCompany(id,current_user_id){
	getRecordBy('Company',{id:id,NotFilterFields:true},function(data){
		Vue.set(vue_title,'Title', data.record.Name);
		Vue.set(vue_record,'values', data.record);

		$.getJSON($SCRIPT_ROOT + '/_get_calendar_events', {'companyId':id},function(data2) {
			Vue.set(vue_schedule,'events',data2.result)
		});

	$.getJSON($SCRIPT_ROOT + '/_get_professional_list', {'CompanyId': id },function(data) {
		Vue.set(vue_schedule,'values', data.result);
		Vue.set(vue_schedule,'current_user_id', current_user_id);
		Vue.set(vue_schedule,'user_type', vue_user_menu.current_user_type);
	});

	});
}


function setProffesional(id,current_user_id,add_activities){
	getRecordBy('User',{id:id,NotFilterFields:true},function(data){
		Vue.set(vue_title,'Title', data.record.Name);
		Vue.set(vue_record,'values', data.record);

		$.getJSON($SCRIPT_ROOT + '/_get_calendar_dates', {'id':id,'AddActivities': add_activities},function(data1) {
			Vue.set(vue_schedule,'values',data1.result)
			Vue.set(vue_schedule,'profId',id)
			Vue.set(vue_schedule,'profName',data.record.Name)
			Vue.set(vue_schedule,'current_user_id',current_user_id)
		});

		$.getJSON($SCRIPT_ROOT + '/_get_calendar_events', {'profId':id},function(data2) {
			Vue.set(vue_schedule,'events',data2.result)
		});

        $.getJSON($SCRIPT_ROOT + '/_get_favorite', {'favId': id} ,function(data2) {
            Vue.set(vue_record,'favorite', data2.result);
        });

		/*getRecordBy('UserFavorite',{UserId: current_user_id, FavoriteId: data.record.id},function(recordFav){
			if (recordFav && recordFav.record && recordFav.record.Checked){
				Vue.set(vue_record,'favorite', 'Eliminar de Favoritos');
				Vue.set(vue_record,'classname', 'btn btn-danger btn-rounded waves-effect waves-light m-t-20');
			}
		}); */
		getRecordBy('Company',{id: data.record.CompanyId},function(company){
			Vue.set(vue_title,'companyName', company.record.Name);
			Vue.set(vue_title,'companyId', data.record.CompanyId);
			/*if (!data.record.Email){record_email.innerHTML = company.Email;}
			if (!data.record.Phone){record_phone.innerHTML = company.Phone;}
			if (!data.record.Address){record_address.innerHTML = company.Address;}
			if (!data.record.City){record_city.innerHTML = company.City;} */
		});

	});
}


function showNotes(){
	var id = document.getElementById('id');
	var name = document.getElementById('Name');
	vars = {Template: 'usernote.html','custId':id.value,'custName': name.value}
	getTemplate(vars)
}

function setActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId){
	vue_record.record.Status = 0;
	vue_record.record.Type = 0;
	vue_record.record.Schedules.push({'StartTime': StartTime,'TransDate': TransDate, 'EndTime': EndTime})
	//updateLinkTo()
}


function createActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId){
	vars = {Template: 'activityform.html',Table:'Activity'}
	getTemplate(vars,function(){
		values = {ProfId :ProfId,CompanyId: CompanyId,CustId: CustId}
		getRecord({TableName:'Activity'},function (data){
			Vue.set(vue_record,'table', 'Activity');
            setVue(data,data.canEdit,data.canDelete);
			setCustomVue('activityform.html',data.record,'Activity')
			vue_title.Title = 'Nuevo Actividad'
			setActivity(TransDate,StartTime,EndTime);
		},values)
	})
}

function setCustomerToEvent(id){
    $.getJSON($SCRIPT_ROOT + '/_set_cust_to_event',{id: id}, function(data) {
      	res = data.result['res'];
      	if (res){
			vue_event.events[id][0].Status = data.result.label;
			if (data.result.st==1){
				vue_event.events[id][0].Persons += 1;
				vue_event.events[id][0].StatusValue = 1;
			}else{
				vue_event.events[id][0].StatusValue = 0;
				vue_event.events[id][0].Persons += -1;
			}
	  	}else{
			alert(data.result['Error']);
		};
    });

}

function newUserNote(custId){
	vars = {Template: 'recordform.html',Table:'UserNote',RecordId:''}
	getTemplate(vars,function(){
		getRecord({TableName:'UserNote'},function (data){
			Vue.set(vue_record,'values', data);
			Vue.set(vue_record,'table', 'UserNote');
			Vue.set(vue_buttons,'canEdit', data.canEdit);
			Vue.set(vue_buttons,'canDelete', data.canDelete);
			vue_record.values.record.UserId = custId;
			vue_title.Title = 'Ingresar Nota'
		})
	})
}

function setNotificationRead(id){
    $.getJSON($SCRIPT_ROOT + '/_set_notification_read',{id: id}, function(data) {
    	getNotificationsList();
    });
}


function getTemplateNotification(){
	vars = {'Name':'Notificaciones','Table':'Notification','Template':'notification.html'}
	getTemplate(vars,function(){
		vue_title.Title = vars.Name;
	});
}

function getNotificationsList(){
	div = document.getElementById('notifications-menu');
	if (div){
		$.getJSON($SCRIPT_ROOT + '/_get_notifications',{}, function(data) {
			Vue.set(vue_notifications,'values',data.result.values)
			Vue.set(vue_notifications,'cnt',data.result.cnt)
			notif_dash = document.getElementById('notifications');
			if (notif_dash){
				Vue.set(vue_dashboard_ntf,'values',data.result.values)
				Vue.set(vue_dashboard_ntf,'cnt',data.result.cnt)
			}
			if (data.result.cnt>0){
				Vue.set(vue_notifications,'news',data.result.cnt + ' notificaciones nuevas')
				if (notif_dash){
					Vue.set(vue_dashboard_ntf,'news',data.result.cnt + ' notificaciones nuevas')
				}
			}else{
				Vue.set(vue_notifications,'news','No hay nuevas notificaciones')
				if (notif_dash){
					Vue.set(vue_dashboard_ntf,'news','No hay nuevas notificaciones')
				}
			}
		});
	}
}

function getMyFunctionReady(){
	getNotificationsList();
}

function updateNotificationsList(){
	Vue.set(vue_dashboard_ntf,'values',vue_notifications.values)
	Vue.set(vue_dashboard_ntf,'cnt',vue_notifications.cnt)
	Vue.set(vue_dashboard_ntf,'news',vue_notifications.news)
}

function showDashboard(){
	getTemplate({'Template':'container.html'},function(){
		updateNotificationsList();
	});
}

function setVueDashboard(){
	$.getJSON($SCRIPT_ROOT + '/_get_current_date',{}, function(data) {
		Vue.set(vue_dashboard,'currentdate',data.result);
	});
}

function getEventList(){

	vars['OrderBy'] = 'TransDate';
	Vue.set(vue_recordlist,'table', 'Activity');
	Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	$.getJSON($SCRIPT_ROOT + '/_event_list', {},function(data) {
		Vue.set(vue_recordlist,'values', data.result);
	});
}


function showEvent(id){

	var titleName = vue_title.Title;
    var moduleNr = vue_title.moduleNr;
    var index = vue_title.indexNr ;

    var vars = {Template: 'event.html',Table: 'Activity', id: id}
	getTemplate(vars,function (){
		$.getJSON($SCRIPT_ROOT + '/_get_calendar_events', {'eventId':id},function(data) {
			Vue.set(vue_event,'events', data.result);
			for (index in data.result){
    			Vue.set(vue_event,'ProfName', data.result[index][0].ProfName);
                vue_title.Title = data.result[index][0].Comment;
			}
		});
        vue_title.moduleNr = moduleNr;
        vue_title.indexNr = index;
		vue_title.tableName = titleName;
	});
}

function cancelActivity() {
    var fields = {}
	_id = vue_record.values.record.id;
	messages.error_msg = '';
	if (vue_record.values.record.Status==2){
		messages.error_msg = 'Actividad ya cancelada';
		return;
	}
    if (_id){
		fields['id'] = _id;
		$.getJSON($SCRIPT_ROOT + '/_cancel_activity', fields, function(data) {
		  if (data.result['res']){
			  setMessageTimeout('Actividad Cancelada')
			  vue_record.values.record.syncVersion = data.result['syncVersion'];
			  vue_record.values._state = 1
			  vue_record.values.record.Status = 2
			  Vue.set(vue_buttons,'id', data.result.id);
			  Vue.set(vue_buttons,'Status', 2);
		  }else{
			  messages.error_msg = data.result['Error'];
		  }
		});
	}else{
	  messages.error_msg = 'No se puede cancelar';
	}
};

function setCustomVue(TemplateName,record,Table){
	if (TemplateName=='activityform.html'){
		Vue.set(vue_buttons,'id', record.id);
		Vue.set(vue_buttons,'Status', record.Status);
		Vue.set(vue_activity,'record',record)
		if (record && record.OnlinePayment && record.Price){
		    Vue.set(vue_activity,'ShowPayment',true);
		}
		if (record.OnlinePayment==1){
			$.getJSON($SCRIPT_ROOT + '/_get_payment', {'activityId': record.id, 'userId': record.CustId,'companyId': record.CompanyId}
				, function(data) {
				Vue.set(vue_activity,'Paid',data.result.res)
				if (!data.result.res){
					Vue.set(vue_activity,'KeyPayco',data.result.KeyPayco)
				}
			});
		}
	}
	if (record.Favorite && record.Favorite==1){
		Vue.set(vue_record,'favorite', 'Eliminar de Favoritos');
		Vue.set(vue_record,'classname', 'btn btn-danger btn-rounded waves-effect waves-light m-t-20');
	}
}

function getCustomerList(table,fields,favorite,limit,order_by,desc,columns){

	var vars = {'Table': table,'Fields': fields, 'favorite': favorite,'Columns': columns}
	if (limit) {vars['Limit'] = limit;}
	if (order_by) {vars['OrderBy'] = order_by;}
	if (desc) {vars['Desc'] = desc;}
	Vue.set(vue_recordlist,'table', table);
	Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	Vue.set(vue_recordlist,'user_id', vue_user_menu.current_user_id);
	$.getJSON($SCRIPT_ROOT + '/_customer_list', vars ,function(data) {
		Vue.set(vue_recordlist,'values', data.result.records);
		Vue.set(vue_recordlist,'filters', data.result.filters);
		Vue.set(vue_recordlist,'filtersNames', data.result.filtersNames);
	});
}

function setServicePrice(){
	service_id = vue_record.values.record.ServiceId;
	if (!service_id){
	    vue_record.values.record.Price = null;
	    return;
	}
	$.getJSON($SCRIPT_ROOT + '/_get_service_price', {'ServiceId': service_id},function(data) {
		if (data.result){
			vue_record.values.record.Price = data.result;
		}else{
			vue_record.values.record.Price
		}
	});
}

function getTemplateM(vars){
	OpenCloseMenu();
	getTemplate(vars,function(){
		vue_title.Title = vars['Name'];
		runSearchBoxOnKey()
	});
}

function getProfessionals(fav){
	var vars = {'Table': 'User', 'favorite': fav, 'Template': 'professional_icon.html', 'Name':'Profesionales'};
	getTemplateM(vars)
}

function getServices(){
	var vars = {'Table': 'Service', 'Template': 'service.html', 'Name':'Servicios'};
	getTemplateM(vars)
}

function getProfServices(){
	var vars = {'Table': 'UserService', 'Template': 'userservice.html', 'Name':'Servicios por Profesional'};
	getTemplateM(vars)
}

function getPayments(){
	var vars = {'Table': 'Payment', 'Template': 'payment.html', 'Name':'Pagos'};
	getTemplateM(vars)
}

function getCustomers(fav){
	var vars = {'Table': 'User', 'Template': 'customer.html', 'Name':'Clientes','favorite': fav, 'TemplateForm':'customerform.html'};
	getTemplateM(vars)
}

function getCompanies(){
	var vars = {'Table': 'Company', 'Template': 'company.html', 'Name':'Empresas'};
	getTemplateM(vars)
}

function getUsers(){
	var vars = {'Table': 'User', 'Template': 'users.html', 'Name':'Usuarios'};
	getTemplateM(vars)
}

function getCalendarView(user_id,user_name){
	var vars = {'Template': 'calendar.html', 'Name':'Calendario','UserId': user_id,'UserName': user_name};
	getTemplateM(vars)
}

function getMySchedule(user_id){
	var vars = {'Template': 'myschedule.html', 'Name':'Vista de Lista','profId': user_id };
	getTemplateM(vars)
}

function getActivities(user_id){
	var vars = {'Table':'Activity', 'Template': 'activity.html', 'Name':'Todas las actividades','TemplateForm':'activityform.html'};
	getTemplateM(vars)
}

function getEvents(){
	var vars = {'Table':'Activity', 'Template': 'events.html', 'Name':'Cursos y Eventos'};
	getTemplateM(vars)
}

function getNotifications(){
	var vars = {'Table':'Notification', 'Template': 'notification.html', 'Name':'Notificaciones'};
	getTemplateM(vars)
}

function getNewUsersReport(){
	var vars = {'ReportClass':'NewUsers', 'Template': 'report.html', 'Name':'Nuevos usuarios por mes'};
	getTemplateM(vars)
}


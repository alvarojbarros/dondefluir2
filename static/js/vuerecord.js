Vue.config.devtools = true;

var vue_buttons = new Vue({
  el: '#div-buttons',
  data: {
    canEdit: '',
    canDelete: '',
    id: '',
    Status: '',
  },
})

var vue_record = new Vue({
  el: '#recordFields',
  data: {
    values: '',
    record: '',
    links: '',
    fields: '',
    events: '',
    table: '',
    oldRecord: '',
    favorite: '',
    classname: '',
    current_user_type: '',
  },

  watch: {
      values: {
          handler: function (val, oldVal) {
            if (val._state==1){
                res = ''
                for (k in val.recordTitle){
                    fieldname = val.recordTitle[k];
                    fieldvalue = val.record[fieldname];
                    linkto = val.links[fieldname]
                    if (linkto){
                        linkvalue = linkto[fieldvalue]
                        if (linkvalue){
                            fieldvalue=linkvalue[0];
                        }
                    }
                    if (fieldvalue){
                        if (res){res = res.concat(' - ')}
                        res = res.concat(fieldvalue);
                    }
                }
                vue_title.Title = res;
            }else{
                vue_title.Title = 'Nuevo Registro'
            }
          },
          deep: true
       },
    },
	updated: function () {
        if (this.record){
            for (fieldname in this.record){
                if (this.oldRecord[fieldname]!=this.record[fieldname]){
                    if (this.events[fieldname] && this.events[fieldname].AfterChange){
                        var call_function = new Function(fieldname, this.events[fieldname].AfterChange);
                        call_function(fieldname);
                    }
                }
            }
            this.oldRecord = $.extend(true,{},this.record)
        }
	},
})


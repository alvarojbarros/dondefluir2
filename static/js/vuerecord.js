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

        if (this.values && this.values.record){
            for (fieldname in this.values.record){
                if (this.oldRecord[fieldname]!=this.values.record[fieldname]){
                    if (this.values.fields[fieldname] && this.values.fields[fieldname].AfterChange){
                        var call_function = new Function(this.values.fields[fieldname].AfterChange);
                        call_function();
                    }
                }
            }
            this.oldRecord = $.extend(true,{},this.values.record)
        }
	},
})


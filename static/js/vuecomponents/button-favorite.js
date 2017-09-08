Vue.config.devtools = true;

Vue.component('button-favorite',{
  props: ['record_id','button_class','favorite'],
  name: 'button-favorite',
  template: '' +
            '<button type="button" id="Favorite"  ' +
            '    :class="isFavorite" v-on:click="setFavorite"> ' +
            '    <span class="btn-label"> ' +
            '        <i class="fa fa-heart"></i> ' +
            '    </span>{{getLabel}} ' +
            '</button> ',
  methods: {
    call_onclick: function () {
    }
  },
  computed: {
    isFavorite: function(){
        if (this.favorite){
            return "btn btn-danger btn-rounded waves-effect waves-light m-t-20";
        }
        return "btn btn-primary btn-rounded waves-effect waves-light m-t-20";

    },
    getLabel: function(){
        if (this.favorite){
            return "Eliminar de Favoritos";
        }
        return "Agregar a Favoritos";
    }
  },
  methods: {
    setFavorite: function () {
        $.getJSON($SCRIPT_ROOT + '/_set_favorite',{favId: this.record_id}, function(data) {
            if (data.result['res']==true){
                  if (data.result['Status']==true) {
                        Vue.set(vue_record,'favorite',true);
                  }else{
                        Vue.set(vue_record,'favorite',false);
                  }
            }
        });

    }
  }
})

//btn btn-primary btn-rounded waves-effect waves-light m-t-20
//btn btn-danger btn-rounded waves-effect waves-light m-t-20
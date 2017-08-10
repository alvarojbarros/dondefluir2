Vue.config.devtools = true;

var vue_activity = new Vue({
  el: '#activity-payment',
  data: {
    Paid: '',
    record: '',
    KeyPayco: '',
  },
  methods: {
    getScript: function(params,KeyPayco) {
			return $(
				'<script src="https://s3-us-west-2.amazonaws.com/epayco/v1.0/checkoutEpayco.js" ' +
				'    class="epayco-button" ' +
				'    data-epayco-key="' + KeyPayco + '"' +
				'    data-epayco-amount="' + params.Price + '"' +
				'    data-epayco-name="Donde Fluir ' + params.Comment + '"' +
				'    data-epayco-description="' + params.Description + '"' +
				'    data-epayco-currency="cop" ' +
				'    data-epayco-country="co" ' +
				'    data-epayco-test="true" ' +
				'    data-epayco-response="'+ window.location.href.replace('#','') + 'epayco/' + params.id + '"' +
				'    data-epayco-confirmation="https://ejemplo.com/confirmacion" > <' + '/script>')
		}
	},
	mounted: function () {
		$('#form-activity').html(this.getScript(this.record,this.KeyPayco))
	},
	updated: function () {
		$('#form-activity').html(this.getScript(this.record,this.KeyPayco))
	}

})

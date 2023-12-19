odoo.define('meta_request_button.website_product_request', function (require) {
  "use strict";
  
  var publicWidget = require('web.public.widget');
  var session = require('web.session');
  var html = document.documentElement;
  var website_id = html.getAttribute('data-website-id');


  publicWidget.registry.AddToRequest = publicWidget.Widget.extend({
    selector: '.js_main_product',
    events: {
      'click #add_to_request ': '_onClickAddToRequest'
    },
    _onClickAddToRequest: function (ev) {
      var productDiv = $(ev.currentTarget).parents('.js_main_product');
      var request_info = {};
      request_info.id = productDiv.children('input[name="product_id"]').val();
      request_info.template_id = productDiv.children('input[name="product_template_id"]').val();
      request_info.quantity = productDiv.find('input[name="add_qty"]').val();
      request_info.user_id = session.user_id;
      request_info.website_id = website_id;
      request_info.template_info = productDiv.children('input[name="product_categ"]').val();
      request_info.template_name = productDiv.children('input[name="product_name"]').val();
      console.log('request_info', request_info);
      console.log('rakin',request_info.template_info);
      
      
      // CHECKING IF USER IS LOGGED IN
      if (!session.user_id) {
        console.log("window.location ---------> ", window.location)
        var redirect_url = _.string.sprintf('%s/web/login?redirect=%s',
          window.location.origin,
          encodeURIComponent(window.location.href)
          
        );
        // Redirect to login page if not logged in
        window.location = redirect_url 
        return;
      }

      var msg = ""
      if (request_info.template_info == 'Local'){
        msg = "আপনি কি \""+ request_info.template_name +"\" বইটি সংগ্রহের জন্য অনুরোধ জানাতে চাইছেন?";
      }
      else{
        msg = "\""+request_info.template_name + "\" বইটি সংগ্রহের অনুরোধ জানাতে অগ্রিম অর্থ পরিশোধ করার প্রয়োজন হতে পারে। আপনি কি বইটি সংগ্রহের জন্য অনুরোধ জানাতে চাইছেন?";
      }
 

      Swal.fire({
        title: 'বই সংগ্রহের অনুরোধ',
        text: msg,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#38b000',
        cancelButtonColor: '#c1121f',
        confirmButtonText: 'হ্যা!',
        cancelButtonText: 'না!'
        
      }).then((result) => {
        if (result.isConfirmed) {
          const loading = Swal.fire({
            title: "Loading...",
            text: "Please wait while we process your request",
            icon: "info",
            showConfirmButton: false,
            showCancelButton: false,
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                Swal.showLoading()
              }
          });
          this._rpc({
            route: "/meta_product_requests/update_request_json",
            params: {
              user_id: request_info.user_id,
              product_id: request_info.id,
              quantity: request_info.quantity,
              website_id : request_info.website_id
            },
            
          }).then(function (data) {           
            if(data){
            loading.close();
            console.log("called");
                Swal.fire(
                  'অনুরোধ বার্তা!',
                  data['text'],
                  data['state'],
                  
                )
            }
          });
          
        }
      })
    },
  });
  return publicWidget.registry.AddToRequest;
});
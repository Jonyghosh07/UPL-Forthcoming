odoo.define('meta_forthcoming_books.website_forthcoming', function (require) {
    'use strict';
    var Animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    let core = require("web.core");
    var ajax = require('web.ajax');
    var session = require('web.session');
    var html = document.documentElement;
    var website_id = html.getAttribute('data-website-id');

    Animation.registry.get_forthcoming_books = Animation.Class.extend({
        selector: '.forthcoming_carousel_template',
        events: {
            "click .add_to_cart": "_onClickAddToRequest",
            "click .js_slide_prev_forth": "_onSlidePrev",
            "click .js_slide_next_forth": "_onSlideNext",
        },

        init: function () {
            this._super.apply(this, arguments);
            this.currentSlide = 0;
            this.imageDoubleCount = 5;
        },

        start: function (ev) {
            console.log("Start function is called");
            var self = this;
            // const productTemplateId = $("input.product_template_id").val();
            // console.log("product_template_id -------> ", productTemplateId)
            var headers = {
                'Content-Type': 'application/json',
                'X-CSRF-Token': core.csrf_token,
            };
            ajax.jsonRpc("/forthcoming_books", 'call', {})
                .then(function (data) {
                    if (data) {
                        self.$target.empty().append(data);
                    }
                });
            ajax.jsonRpc("/forthcoming_books_count", 'call', {})
                .then(function (data) {
                    if (data) {
                        document.querySelector(':root').style.setProperty('--image-count', data);
                    }
                });
        },

        _onSlidePrev: function () {
            console.log("Previous button clicked.....")
            this.currentSlide = (this.currentSlide - 1 + this.imageDoubleCount) % this.imageDoubleCount;
            this._updateSlidePosition();
        },
        _onSlideNext: function () {
            console.log("Next button clicked.....")
            this.currentSlide = (this.currentSlide + 1) % this.imageDoubleCount;
            this._updateSlidePosition();
        },
        _updateSlidePosition: function () {
            // var transformValue = -495 * this.currentSlide;
            var transformValue;
            if (window.innerWidth >= 768) {
                // Desktop view
                transformValue = -600 * this.currentSlide;
            } else {
                // Mobile view
                transformValue = -210 * this.currentSlide;
            }
            this.$('.slide-track_forth').css('transform', 'translateX(' + transformValue + 'px)');
        },

        _onClickAddToRequest: function (ev) {
            var $card = $(ev.currentTarget).closest(".add_to_cart");
            var productDiv = $card.find("input[data-product-id]").data("product-id");
            var user_id = session.user_id
            console.log('product_product id ------------->', productDiv);
            console.log('user_id ------------->', user_id);

            // CHECKING IF USER IS LOGGED IN
            if (!session.user_id) {
                console.log("window.location ----------------> ", window.location)
                var url = "/shop"
                console.log("url ----------------> ", url)
                // User is not logged in, redirect to login page
                var redirect_url = _.string.sprintf('%s/web/login?redirect=%s',
                    window.location.origin,
                    url
                );
                // Redirect to login page
                window.location = redirect_url;
                return;
            }
            ajax.jsonRpc('/productdetails', 'call',{'user_id': user_id, 'product_id': productDiv})
            .then(function(data) {           
                if(data){
                    var msg = "\"" + data['prod_name'] + "\" বইটি সংগ্রহের অনুরোধ জানাতে অগ্রিম অর্থ পরিশোধ করার প্রয়োজন হতে পারে। আপনি কি বইটি সংগ্রহের জন্য অনুরোধ জানাতে চাইছেন?";
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
                            ajax.jsonRpc('/meta_product_requests/update_request_json' , 'call',
                                {
                                    user_id: user_id,
                                    product_id: productDiv,
                                    quantity: 1,
                                    website_id: website_id
                                })
                                .then(function (data) {
                                if (data) {
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
                }
            });
        },
    });
});


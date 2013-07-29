$(document).ready(function() {
  filepicker.setKey("AAO81GwtTTec7D8nH9SaTz");

  function openFilepicker(callback) {
    filepicker.pick({
        services: ['COMPUTER', 'BOX', 'DROPBOX', 'GOOGLE_DRIVE', 'SKYDRIVE', 'URL'],
      },
      function(fpfile){
        callback(fpfile);
      },
      function(fperror){
        console.log(fperror);
        alert(fperror);
      });
  }
  function openImagepicker(callback) {
    filepicker.pick({
        mimetypes: ['image/*'],
        services: ['COMPUTER', 'FACEBOOK', 'IMAGE_SEARCH', 'INSTAGRAM', 'URL'],
      },
      function(fpfile){
        callback(fpfile);
      },
      function(fperror){
        console.log(fperror);
        alert(fperror);
      });
  }

  $('form:not(.search-box)').each(function(ind, this_form) {

    $(this_form).submit(function(e) {
      var self = this;
      var ajax_info = {
        type : $(this_form).attr('method'),
        url  : $(this_form).attr('action'),
        data : $(this_form).serialize(),
        complete : function(jqxhr, statusStr) {
          // enable submit button 
          $('input[type=submit]', self).removeAttr('disabled');
        },
        success : function(data, statusStr, xhr) {
          if (!data.success){
            // RENDER ERRORS ON THE FORM
            _.each(data.errors, function(val, key, ind) {
              if(key==='__all__') {
                $('.form-error.field-all', self).html(val.join('<br />'));
              } else {
                $('.form-error.field-name-'+key, self).html(val.join('<br />'));
              }
            });
          } else {
            // COMPLETE THE FRONTEND SUCCESS ACTIONS
            if (typeof(data.redirect_to) !== 'undefined') {
              location.href = data.redirect_to;
            } else {
              if (typeof(data.refresh) !== 'undefined' && data.refresh) {
                location.reload(true);
              } else {
                alert("Form submitted! But... now what do I do...")
              }
            }
          }
        },
        error: function(jqxhr, statusStr, errorThrown) {
          alert('Form didn\'t submit properly... Well this is awkward.');
        }
      };
      $.ajax(ajax_info);
      // disable submit button 
      $('input[type=submit]', this).attr('disabled', 'disabled');
      $('.form-error', this).html("");

      return false;

    });

  });

  // image upload buttons
  $('.btn.upload-img, .btn.upload-file').click(function(e) {
    // open file or img picker, depending on the classname
    if($(this).hasClass('upload-file')){
        openFilepicker(function(file){
          var fieldId = String(e.target.getAttribute("data-name"));
          $('input[type="hidden"][name="'+fieldId+'"]').val(file.url);
        });
    } else if ($(this).hasClass('upload-img')) {
        openImagepicker(function(file){
          var fieldId = String(e.target.getAttribute("data-name"));
          $('input[type="hidden"][name="'+fieldId+'"]').val(file.url);
        });
    } else {
        // this case wont happen
        alert("Not a file, not an image, so this is broken.");
    }

    e.preventDefault();
  });




});

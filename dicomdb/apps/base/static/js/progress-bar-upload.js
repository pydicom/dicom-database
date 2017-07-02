$(function () {

  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  $("#fileupload").fileupload({
    dataType: 'json',
    sequentialUploads: true,

    start: function (e) {
      $("#modal-progress").show();
      $("#fade").show()
      $("#loadfish").show()
    },

    stop: function (e) {
      $("#modal-progress").hide();
      $("#fade").hide()
      $("#loadfish").hide()
    },

    progressall: function (e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      var strProgress = progress + "%";
      $(".progress-bar").css({"width": strProgress});
      $(".progress-bar").text(strProgress);
    },

    done: function (e, data) {
      if (data.result.is_valid) {
        console.log(data);

        // Valid
        $("#gallery tbody").prepend(
          "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
        )

        $("#next-steps").show();

        // Invalid
        } else {
        $("#gallery tbody").prepend(
            "<tr><td><p class='alert alert-info'>" + data.result.name + " is not valid format.</p></td></tr>"
        )
      }
    }

  });

});

$("#fileupload").fileupload({
  dataType: "json",
  add: function(e, data) {
    data.context = $('<p class="file">')
      .append($('<a target="_blank">').text(data.files[0].name))
      .appendTo(".attachment");
    data.submit();
  },
  progress: function(e, data) {
    var progress = parseInt((data.loaded / data.total) * 100, 10);
    data.context.css("background-position-x", 100 - progress + "%");
  },
  done: function(e, data) {
    data.context
      .addClass("done")
      .find("a")
      .prop("href", data.result.files[0].url);
  }
});
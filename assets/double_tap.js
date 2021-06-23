document.addEventListener('DOMContentLoaded', function(){
    var isZoomIn=true;
    var zoom=-1000;
    var tap_counter=0;
    setTimeout(function(){
  var myPlot = document.getElementById('3D-model-light');
  var tapedTwice = false;

  var delay;
  var longpress = 1000;
  myPlot.addEventListener("touchstart", doubleTapHandler);
  function doubleTapHandler(event) {
    var touches = event.changedTouches,
        first = touches[0],
        type = '';

      if(!tapedTwice) {
          tapedTwice = true;
          setTimeout( function() {tapedTwice = false;}, 300 );
          return false;
      }
      event.preventDefault();
      //action on double tap goes

      tap_counter=tap_counter+1;
      if (tap_counter < 2){
          isZoomIn = true;
          zoom = -200;

      }
      else{
          isZoomIn = false;
          tap_counter = 0
          zoom = -200;

      }


      var simulatedEvent = new WheelEvent('wheel', {
               bubbles: true, // only bubbles and cancelable
               cancelable: true, // work in the Event constructor
               isTrusted: true,
               screenX: first.screenX,
               screenY: first.screenY,
               clientX: first.clientX,
               clientY: first.clientY,
               deltaY: zoom,
             });
             first.target.dispatchEvent(simulatedEvent);
             event.preventDefault();
      //alert('You tapped me Twice !!!');
   }
}, 2000);

});

document.addEventListener('DOMContentLoaded', function(){
    setTimeout(function(){
  var myPlot = document.getElementById('3D-model-light');
  myPlot.addEventListener("touchend", layoutHandler);
  function layoutHandler(event) {
    var touches = event.changedTouches,
        first = touches[0],
        type = '';

      var simulatedEvent = new WheelEvent('wheel', {
               bubbles: true, // only bubbles and cancelable
               cancelable: true, // work in the Event constructor
               isTrusted: true,
               screenX: first.screenX,
               screenY: first.screenY,
               clientX: first.clientX,
               clientY: first.clientY,
               deltaY: 1,
             });
             first.target.dispatchEvent(simulatedEvent);
             event.preventDefault();
   }
}, 2000);
});
document.addEventListener('DOMContentLoaded', function(){
    setTimeout(function(){
  var myPlot = document.getElementById('map-2D-arrow');
  myPlot.addEventListener("touchstart", ignore_event);
  function ignore_event(event) {
      event.preventDefault();
   }
}, 2000);

});
document.addEventListener('DOMContentLoaded', function(){
    setTimeout(function(){
  var myPlot = document.getElementById('map-2D-arrow');
  myPlot.addEventListener("touchmove", ignore_event);
  function ignore_event(event) {
      event.preventDefault();
   }
}, 2000);
});

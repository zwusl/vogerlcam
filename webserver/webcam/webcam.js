$(document).ready(function(){


/*
    $.getJSON( "/webcam/checkreload.py", {uhrzeit: uhrzeit}, function( data ) {
        var items = [];
        $.each( data, function( key, val ) {
            //items.push(key + "xxx" + val + "<br>");
            items.push(val);
        });
        $(".uhrzeit").html(items[1]);
        $(".currentimg").attr("src",items[0]);

        //$( "body" ).append( items );
    });
*/


      
function myupdate() {
    var source = '/webcam/webcam_0.jpeg',
    timestamp = (new Date()).getTime(),
    newUrl = source + '?_=' + timestamp,
    doupdate = 0;
    
    //alert("abc");
    
    uhrzeit = document.getElementsByClassName('uhrzeit')[0].innerHTML;


    $.getJSON( "/webcam/checkreload.py", {uhrzeit: uhrzeit, timestamp: timestamp}, function( data ) {
        var items = [];
        $.each( data, function( key, val ) {
            //items.push(key + "xxx" + val + "<br>");
            items.push(val);
        });
        doupdate = items[0];
        //if (items[1]>items[2]){
        if (doupdate=="neu") {
            document.getElementById("webcam").src = newUrl;
            $(".uhrzeit").html(items[1]);
            //$(".uhrzeit2").html(items[2]);
            //$(".doupdate").html(doupdate + "1 " + timestamp);
        }
        else {
            $(".uhrzeit").html(items[1]);
            //$(".uhrzeit2").html(items[2]);
            //$(".doupdate").html(doupdate + "0 " + timestamp);        
        }
        uhrzeit = items[2];

        //$( "body" ).append( items );
    });


    //setTimeout(update,3000);
    //window.setTimeout(function() { myupdate(); }, 3000);
    setTimeout(myupdate, 3000);
}


    myupdate();


});
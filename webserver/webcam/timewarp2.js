$(document).ready(function(){
    

    $(".navigate").click(function(){
    
        
        var cur = document.getElementsByClassName('current')[0].innerHTML;
        var action = $(this).val();
        
                
        var uhrzeit = document.getElementsByClassName('uhrzeit')[0].innerHTML;
        

        $.getJSON( "/webcam/timewarp2.py", {current: cur, action: action, uhrzeit: uhrzeit}, function( data ) {
            var items = [];
            $.each( data, function( key, val ) {
                //items.push(key + "xxx" + val + "<br>");
                items.push(val);
            });
            $(".current").html(items[0]);
            $(".uhrzeit").html(items[1]);
            $(".currentimg").attr("src",items[0]);

            //$( "body" ).append( items );
        });
    });
    
    
    

    $("body").keydown(function(e) {
        var cur = document.getElementsByClassName('current')[0].innerHTML;
        var action = "";
        var uhrzeit = document.getElementsByClassName('uhrzeit')[0].innerHTML;
        if(e.keyCode == 37) { // left
            action = "pd";
        }
        else if(e.keyCode == 39) { // right
            action = "nd";
        }
        else if(e.keyCode == 38) { // up
            action = "pi";
        }
        else if(e.keyCode == 40) { // down
            action = "ni";
        }
        $.getJSON( "/webcam/timewarp2.py", {current: cur, action: action, uhrzeit: uhrzeit}, function( data ) {
            var items = [];
            $.each( data, function( key, val ) {
                //items.push(key + "xxx" + val + "<br>");
                items.push(val);
            });
            $(".current").html(items[0]);
            $(".uhrzeit").html(items[1]);
            $(".currentimg").attr("src",items[0]);

            //$( "body" ).append( items );
        });
        
    });



    $('.currentimg').click(function(e) {
    var offset = $(this).offset();
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var action;
    var updown;
    var leftright;
    
    //alert(e.pageX - offset.left);
    //alert(e.pageY - offset.top);
    //var img = document.getElementById('imageid'); 
    var img = document.getElementsByClassName('currentimg')[0];
    //or however you get a handle to the IMG
    var width = img.clientWidth;
    var height = img.clientHeight;
    //alert(width);
    //alert(height);
    if (y<(height/2) && ( ( x > y && x < (width/2) ) || ((width -x) > (y) && x > width/2) ) )
    {
        action = "pi";
    }
    else if (y>(height/2) && ( ( x > (height - y) && x < (width/2) ) || ((width -x) > (height-y) && x > width/2) ) )
    {
        action = "ni";
    }
    else if (x<(width/2))
    {
        action = "pd";
    }
    else
    {
        action = "nd";
    }

    var cur = document.getElementsByClassName('current')[0].innerHTML;

                
    var uhrzeit = document.getElementsByClassName('uhrzeit')[0].innerHTML;
    

    $.getJSON( "/webcam/timewarp2.py", {current: cur, action: action, uhrzeit: uhrzeit}, function( data ) {
        var items = [];
        $.each( data, function( key, val ) {
            //items.push(key + "xxx" + val + "<br>");
            items.push(val);
        });
        $(".current").html(items[0]);
        $(".uhrzeit").html(items[1]);
        $(".currentimg").attr("src",items[0]);

        //$( "body" ).append( items );
    });


  });
    

});
      

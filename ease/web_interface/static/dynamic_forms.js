


function dynamic_form_controller(){
    console.log(dfc_prefix);
    console.log(dfc_fields);
    console.log(dfc_replace);



    var next_contents_no = $('input[name=tg-TOTAL_FORMS]').val();


    $("#add_trigger_btn").click(function(){

        if (dfc_fields.length != dfc_replace.length){
            console.log("ARGUMENT LENGTH ERROR");
        }

        var new_contents = $("#contents_section").children().last().clone();

        
        // new_contents.find("input[id*=id_tg-][id*=-new_name]").attr('id','id_tg-'+next_contents_no.toString()+'-new_name');
        // new_contents.find("input[name*=tg-][name*=-new_name]").attr('name','tg-'+next_contents_no.toString()+'-new_name');
        // new_contents.find("input[name*=tg-][name*=-new_name]").val("");

        // new_contents.find("select[id*=id_tg-][id*=-new_pv]").attr('id','id_tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents.find("select[name*=tg-][name*=-new_pv]").attr('name','tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents.find("select[name*=tg-][name*=-new_pv]").val(-1);








        for (var i = 0; i < dfc_fields.length; i++){
            find = "[id*=id_"+dfc_prefix+
                "-][id*=-"+dfc_fields[i]+"]"
            update = "id_"+dfc_prefix+
                "-"+next_contents_no.toString()+
                "-"+dfc_fields[i]
            new_contents.find(find).attr('id', update);

            find = "[name*="+dfc_prefix+
                "-][name*=-"+dfc_fields[i]+"]"
            update = dfc_prefix+
                "-"+next_contents_no.toString()+
                "-"+dfc_fields[i]
            new_contents.find(find).attr('name',update);

            find = "[name*="+dfc_prefix+
                "-][name*=-"+dfc_fields[i]+"]"

            new_contents.find(find).val(dfc_replace[i]);
        }

        // new_contents.find("select[id*=id_tg-][id*=-new_pv]").attr('id','id_tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents.find("select[name*=tg-][name*=-new_pv]").attr('name','tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents.find("select[name*=tg-][name*=-new_pv]").val(-1);


       
        // new_contents
        //     .find("[id*=id_tg-][id*=-new_name]")
        //         .attr('id','id_tg-'+next_contents_no.toString()+'-new_name');
        // new_contents
        //     .find("[name*=tg-][name*=-new_name]")
        //         .attr('name','tg-'+next_contents_no.toString()+'-new_name');
        // new_contents
        //     .find("[name*=tg-][name*=-new_name]")
        //         .val("");

        // new_contents
        //     .find("[id*=id_tg-][id*=-new_pv]")
        //         .attr('id','id_tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents
        //     .find("[name*=tg-][name*=-new_pv]")
        //         .attr('name','tg-'+next_contents_no.toString()+'-new_pv');
        // new_contents
        //     .find("[name*=tg-][name*=-new_pv]")
        //         .val(-1);




        $("#contents_section").append(new_contents);

        var cache = $("input[name=tg-TOTAL_FORMS]").val();
        console.log(cache);
        $("input[name=tg-TOTAL_FORMS]").val(Number(cache)+1);

        next_contents_no ++;
        console.log("click2");


        new_contents.find(".delete-btn").click(delete_handler);


    });



    function delete_handler() {
        if ( $('input[name=tg-TOTAL_FORMS]').val() <= 1 ){
            return;
        }
        //var test = $(this);
        console.log(this);
        console.log($(this));
        $(this).attr('class',"btn btn-danger text-muted")
        //this.innerHTML = "keep this!";
        $(this).parent().parent().remove();
        //console.log($(this)[0].innerHTML); 
        console.log("click_del");
        var cache = $("input[name=tg-TOTAL_FORMS]").val();
        console.log(cache);
        $("input[name=tg-TOTAL_FORMS]").val(Number(cache)-1);
    }


    // handle line deletion

    $(".delete-btn").click(delete_handler);


}
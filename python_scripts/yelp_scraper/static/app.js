var search_link;

function generateLink(event){

    var business_name = document.getElementById("business").value.trim()
    var location = document.getElementById("location").value.trim()

    search_link = "/scrape?search=" + business_name + "&location=" + location

    if(event.keyCode === 13){
         getData(business_name,location);
     }


}

function getData(){
    console.log(search_link);
    var business_name = document.getElementById("business").value.trim()
    var location = document.getElementById("location").value.trim()

    if (business_name === "" && location === ""){
        document.getElementById("business").style.cssText = "border-color: #FD0000; border-width:2px;"
        document.getElementById("location").style.cssText = "border-color: #FD0000; border-width:2px;"

    }

    else if (business_name === "" && location !== ""){
        document.getElementById("business").style.cssText = "border-color: #FD0000; border-width:2px;"
        document.getElementById("location").style.cssText = ""

    }

    else if (business_name !== "" && location === ""){
        document.getElementById("location").style.cssText = "border-color: #FD0000; border-width:2px;"
        document.getElementById("business").style.cssText = ""

    }

    else {
        document.getElementById("location").style.cssText = ""
        document.getElementById("business").style.cssText = ""
        document.getElementById("business").readOnly = true;
        document.getElementById("location").readOnly = true;
        document.getElementById("scrapeSearch").disabled = true;
        document.getElementById("progressBar").style.visibility = "visible";
        document.getElementById("finalResult").innerHTML = "";

        d3.json(search_link).then(function(data){
            var business_name = data["BUSINESS_NAME"];
            var sentiment = data["SENTIMENT"];

            if (business_name != "ERROR"){
            console.log(data);
            document.getElementById("progressBar").style.visibility = "hidden";

            document.getElementById("finalResult").innerHTML = `The general sentiment for ${business_name} is ${sentiment}.`;
            document.getElementById("business").readOnly = false;
            document.getElementById("location").readOnly = false;
            document.getElementById("scrapeSearch").disabled = false;}

            else{
                console.log(data);
                document.getElementById("progressBar").style.visibility = "hidden";
    
                document.getElementById("finalResult").innerHTML = `There was an error retrieving the Yelp data. Please try again.`;
                document.getElementById("business").readOnly = false;
                document.getElementById("location").readOnly = false;
                document.getElementById("scrapeSearch").disabled = false;}

            


    })}

}


if (document.getElementById("progressBar") != null){

    document.getElementById("progressBar").style.visibility = "hidden";
}
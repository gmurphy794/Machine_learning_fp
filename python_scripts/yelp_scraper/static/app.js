var search_link;
var complete;

function generateLink(event){

    var business_name = document.getElementById("business").value.trim()
    var location = document.getElementById("location").value.trim()

    search_link = "/scrape?search=" + business_name + "&location=" + location

    if(event.keyCode === 13){
         getData(business_name,location);
     }
}

function getData(){
    // console.log(search_link);
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
        getPercent();

        d3.json(search_link).then(function(data){
            
            var business_name = data["BUSINESS_NAME"];
            var sentiment = data["SENTIMENT"];
            var business_page = data["BUSINESS_URL"];

            if (business_name != "ERROR"){
            // console.log(data);
            document.getElementById("progressBar").style.visibility = "hidden";

            document.getElementById("finalResult").innerHTML = `The general sentiment for <a href='${business_page}' target='_blank'>${business_name}</a> is ${sentiment}.`;
            document.getElementById("business").readOnly = false;
            document.getElementById("location").readOnly = false;
            document.getElementById("scrapeSearch").disabled = false;
            document.getElementById("business").value = "";
            document.getElementById("location").value = "";
        
            }

            else{
                // console.log(data);
                document.getElementById("progressBar").style.visibility = "hidden";
    
                document.getElementById("finalResult").innerHTML = `There was an error retrieving the Yelp data. Please try again.`;
                document.getElementById("business").readOnly = false;
                document.getElementById("location").readOnly = false;
                document.getElementById("scrapeSearch").disabled = false;
                document.getElementById("business").value = "";
                document.getElementById("location").value = "";
            }

    })}

}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

async function getPercent(){
    complete = 0;
    for (var i = 0; i < 20; i++){
        await sleep(1000);
    d3.json("/percentComplete").then(function(data){

        
                var percent_complete = data["PERCENT_COMPLETE"];
                complete = data["COMPLETE"];
                // console.log(percent_complete);
                // console.log(complete);
                if (complete === 0){
                document.getElementById("progressBar").style.cssText = `width : ${percent_complete}%; height:4px;`}
    })
    if (complete === 1){
        // console.log(complete);
        // console.log("breaking percent loop")
        break;
    }
}
}

if (document.getElementById("progressBar") != null){

    document.getElementById("progressBar").style.visibility = "hidden";
}
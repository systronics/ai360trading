var savePageWE=require('/public/src/nodeSavePageWE');


savePageWE.scrape({ url: "/public/Intraday.mht", path: "intraday.html" }).then(function ()
{
    console.log("ok");
});

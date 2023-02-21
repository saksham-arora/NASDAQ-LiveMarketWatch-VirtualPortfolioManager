function startUpdate() {
  myVar = setInterval(tableUpdate, 5000);
  tableUpdate();
}

function convertPriceToFloat(price)
{
  var floatPrice = parseFloat(price.substring(1,price.length).replace(new RegExp(',', 'g'), ''));
  return floatPrice;
}

function getColor(current, updated, color)
{
   if ( parseFloat(current.toFixed(2)) > parseFloat(updated.toFixed(2)))
    return "#FC8A65";
   else if ( parseFloat(current.toFixed(2)) < parseFloat(updated.toFixed(2)))
    return "#92F15F";

  return color;
}

function getProfitLoss(current, updated)
{
    var pl = parseFloat(updated.toFixed(2)) -  parseFloat(current.toFixed(2));
    return pl;
}

function tableUpdate()
{
   var table = document.getElementById("symboltable");
     
		$.ajax(
    {
			  url: '/symbolsPrice',
			  type: 'GET',
			  success:function(response)
        {
          var updatedTotal = 0;
          var totPL = 0;
		  console.log(response);
          var r = JSON.parse(response);
          for (var i = 1, row; i < table.rows.length-3; i++)
          {
            row = table.rows[i];
            symbol = row.cells[0].innerHTML;
            currentPriceString= row.cells[3].innerHTML;
            currentPrice = convertPriceToFloat(currentPriceString);
            updatedPrice = convertPriceToFloat(r[symbol]);
            row.cells[4].innerHTML = r[symbol];
            var plColor = getColor(currentPrice,updatedPrice, row.cells[4].bgColor);
            row.cells[4].bgColor = plColor;

            shares = parseInt(row.cells[2].innerHTML);
            var updatedValue = updatedPrice*shares;
            var currentValue = currentPrice*shares;
            var pl = getProfitLoss(currentValue, updatedValue);
            row.cells[5].innerHTML = "$" + parseFloat(pl.toFixed(2)).toLocaleString("en-US");
            row.cells[6].innerHTML = "$" + parseFloat(updatedValue.toFixed(2)).toLocaleString("en-US");
            row.cells[5].bgColor = plColor;
            row.cells[6].bgColor = plColor;
         
            totPL = totPL + pl;  
            updatedTotal = updatedTotal + updatedValue;
          }

          var actualTotal = updatedTotal + convertPriceToFloat(document.getElementById("cash").innerHTML);
          document.getElementById("PL").innerHTML = "$" + parseFloat(totPL.toFixed(2)).toLocaleString("en-US");
          document.getElementById("total").innerHTML = "$" + parseFloat(actualTotal.toFixed(2)).toLocaleString("en-US");

          if ( actualTotal > 10000 )
          {
            document.getElementById("total").bgColor = "#92F15F";
            document.getElementById("PL").bgColor = "#92F15F";
          }
          else if ( actualTotal < 10000 )
          {
            document.getElementById("total").bgColor = "#FC8A65";
            document.getElementById("PL").bgColor = "#FC8A65";
          }
          else
          {
            document.getElementById("total").bgColor = "#FAF393";
            document.getElementById("PL").bgColor = "#FAF393";
          }
			  },
			  error: function(error)
        {
				  console.log(error);
			  }
    });
}


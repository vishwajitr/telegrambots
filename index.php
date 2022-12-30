<style>
a.product-block {
    width: 300px;
    float: left;
    background: #fff;
    padding: 50px;
    max-width: 300px;
    height: 300px;
    margin: 10px;
    text-align: center;
    box-shadow: 0px 2px 10px #cccccc;
}
</style>

<?php

    $i=1;
    while ($i<=5) {
      # code...
        $url = 'http://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_electronics_pg_'.$i.'?ie=UTF8&pg='.$i;
            $html= file_get_contents($url);
            $dom = new DOMDocument();
            @$dom->loadHTML($html);
            $xPath = new DOMXPath($dom);
            // echo '<pre>';
            // print_r($dom);

            $classname="a-link-normal";
            // $image_class= 'a-section a-spacing-small';
            // $title_class = 'p13n-sc-truncated';
            // $ratings_class="a-icon-alt";
            // $price_class="p13n-sc-price";
            $elements = $xPath->query("//*[contains(@class, '$classname')]");
            
            echo '<pre>';
            print_r($elements);
            foreach ($elements as $e)
              {
                // print_r($e);
                $lnk = $e->getAttribute('href');
                $e->setAttribute("href", "http://www.amazon.in".$lnk."&tag=sportybruh08-21");
                
                // $product_name = $e->setAttribute("class", "product-name");
                // $product_desc = $e->getAttribute("textContent");

                // echo '<pre>';
                // print_r($e);
                // $current_class = $e->getAttribute('class');
                

                $newdoc = new DOMDocument;
                $e = $newdoc->importNode($e, true);
                // $e->setAttribute('class', $current_class." product-block");

                $newdoc->appendChild($e);
                $html = $newdoc->saveHTML();
                echo $html;
            }
            
            $i++;
           }

?>
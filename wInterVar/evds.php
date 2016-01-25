<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>InterVar-Interpretation of genetic variants by ACMG2015 guideline</title>

    <!-- Bootstrap Core CSS -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link href="css/half-slider.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->

</head>

<body>

    <!-- Navigation -->
<?php        include "nav.html";        ?>
    <!-- Page Content -->
    <div class="container">

        <div class="row">
            <div class="col-lg-12">
                <h1>Interpretation of genetic variants by ACMG2015 guideline</h1>
                <p>InterVar is a bioinformatics software tool for clinical interpretation of genetic variants by the ACMG2015 guideline. The input to InterVar is an annotated file generated from ANNOVAR, while the output of InterVar is the classification of variants into 'Benign', 'Likely benign', 'Uncertain significance', 'Likely pathogenic' and 'Pathogenic', together with detailed evidence code.</p>

                     <HR>
            </div>
                <hr>
            <form enctype="multipart/form-data" action="mlr.php" method="post" bgcolor='#ddddee'>

                <p class="pvs">
                 <input type="checkbox" name="pvs1" value="1"> PVS1: null variant (nonsense, frameshift, canonical +- 2 splice sites, initiation codon, single or multiexon deletion) in a gene where LOF is a known mechanism of disease<br>
                 </p>
                 <p class="pvs">
                 <input type="checkbox" name="ps1" value="1"> PS1: Same amino acid change as a previously established pathogenic variant regardless of nucleotide change<br>
                 <input type="checkbox" name="ps2" value="1"> PS2: De novo (both maternity and paternity confirmed) in a patient with the disease and no family history<br>
                 <input type="checkbox" name="ps3" value="1"> PS3: Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product<br>
                 <input type="checkbox" name="ps4" value="1"> PS4: The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls<br>
                 <!-- <input type="checkbox" name="pp1" value="1"> PP1 (Strong evidence) Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease<br> -->
                 </p>
                 <p class="pm">
                 <input type="checkbox" name="pm1" value="1"> PM1: Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active site of an enzyme) without benign variation<br>
                 <input type="checkbox" name="pm2" value="1"> PM2: Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium<br>
                 <input type="checkbox" name="pm3" value="1"> PM3: For recessive disorders, detected in trans with a pathogenic variant<br>
                 <input type="checkbox" name="pm4" value="1"> PM4: Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants<br>
                 <input type="checkbox" name="pm5" value="1"> PM5: Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before<br>
                 <input type="checkbox" name="pm6" value="1"> PM6: Assumed de novo, but without confirmation of paternity and maternity<br>
                 <!-- <input type="checkbox" name="pp1_m" value="1"> PP1 (Moderate evidence) Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease<br> -->
                 </p>
                 <p class="pp">
                 <input type="checkbox" name="pp1" value="1"> PP1: Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease<br>
                 <input type="checkbox" name="pp2" value="1"> PP2: Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease<br>
                 <input type="checkbox" name="pp3" value="1"> PP3: Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.)<br>
                 <input type="checkbox" name="pp4" value="1"> PP4: Patient's phenotype or family history is highly specific for a disease with a single genetic etiology<br>
                 <input type="checkbox" name="pp5" value="1"> PP5: Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation
                 </p>
                 <p class="bs">
                 <input type="checkbox" name="ba1" value="1"> BA1: Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium<br>
                 </p>
                 <p class="bs">
                 <input type="checkbox" name="bs1" value="1"> BS1: Allele frequency is greater than expected for disorder<br>
                 <input type="checkbox" name="bs2" value="1"> BS2: Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penetrance expected at an early age<br>
                 <input type="checkbox" name="bs3" value="1"> BS3: Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing<br>
                 <input type="checkbox" name="bs4" value="1"> BS4: Lack of segregation in affected members of a family<br>
                 </p>
                 <p class="bp">
                 <input type="checkbox" name="bp1" value="1"> BP1: Missense variant in a gene for which primarily truncating variants are known to cause disease<br>
                 <input type="checkbox" name="bp2" value="1"> BP2: Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern<br>
                 <input type="checkbox" name="bp3" value="1"> BP3: In-frame deletions/insertions in a repetitive region without a known function<br>
                 <input type="checkbox" name="bp4" value="1"> BP4: Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary, splicing impact, etc.)<br>
                 <input type="checkbox" name="bp5" value="1"> BP5: Variant found in a case with an alternate molecular basis for disease<br>
                 <input type="checkbox" name="bp6" value="1"> BP6: Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation<br>
                 <input type="checkbox" name="bp7" value="1"> BP7: A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved<br>
                 </p>


                 <input type="submit" name=".submit" class="btn  btn-default">
                 <input type="reset" name=".reset" class="col-sm-offset-1 btn  btn-default">

              </FORM>

        </div>

        <hr>


    </div>
    <!-- /.container -->
<?php        include "footer.html";        ?>
    <!-- jQuery -->
    <script src="js/jquery.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="js/bootstrap.min.js"></script>

    <!-- Script to Activate the Carousel -->
    <script>
    $('.carousel').carousel({
        interval: 5000 //changes the speed
    })
    </script>

</body>

</html>
//=====================================================================
//=====================================================================
// Preprocesamiento de bases
// Lee, limpia y procesa las bases por separado
// A continuación integra las bases en 3 archivos finales: 
// train, validation y test
//
// Se utilizan las bases del CEMABE, F911 y ENLACE
//
// Última modificación: 11/24/2019
//=====================================================================
//=====================================================================

//Direcciones
gl dir = "E:\Proy_Paola_Salo\Educacion\entrega BM"
gl basesD = "$dir\bases auxiliares\deleteMyFiles"
gl basesA= "$dir\bases auxiliares"
gl basesO= "E:\Proy_Paola_Salo\Educacion\hechosNotables\source"
gl cie = "E:\Proy_Paola_Salo\Educacion\hechosNotables\"
gl f911 = "$cie\source\911 BASICA\"
gl basesAS = "$cie\basesAuxiliares\"
gl source = "$cie\source\"
gl resultados= "$cie\resultados\"

clear all 
set more off 


//===========================================
//===========================================
//  C E M A B E
//===========================================
//===========================================

//Abre y guarda en formato dta
import delimited "$basesO\cemabe_2015_00_csv\TR_CENTROS.csv", clear encoding(utf8) 
save "$basesA\centros.dta", replace

import delimited "$basesO\cemabe_2015_00_csv\TR_CONAFE.csv", clear encoding(utf8) 
save "$basesA\conafe.dta", replace

import delimited "$basesO\cemabe_2015_00_csv\TR_inmuebles.csv", clear encoding(utf8) 
save "$basesA\inmuebles.dta", replace

//Integra las bases
use "$basesA\inmuebles.dta", clear
merge 1:m id_inm using "$basesA\centros.dta", force
gen cct = substr(clave_ct, 1, 10)
drop _merge
duplicates drop cct turno, force
save "$basesA\inmuebles_centros.dta", replace

//********************************
//Limpia y genera nuevas variables
//********************************
use "$basesA\inmuebles_centros.dta", clear
//Nos aseguramos de que sean numericas
destring p3-p364 , replace force

//Eliminamos las variables de dirección del centro de trabajo
drop nom_ent nom_mun nom_loc nombrect p4a p4b p4c p4d p4e p4f p4g p4h p4i p4j p4k

//Limpiamos y creamos variables identificadas como importantes después del EDA
foreach var of varlist p157 p231 p268 p52 /// 
						p62 p72 p82 p92 { 
	replace `var' = . if `var' ==9
}

foreach var of varlist p34 p38 p40 p42 p169 p178 p232 ///
						p236 p292 p294 p295 p48 p49 /// 
						p25 p26 p28 p19 p30 p31 p32 p33 { 
	replace `var' = . if `var' ==999
}

foreach var of varlist p277 p276 p285 p284{ 
	replace `var' = . if `var' ==9999
}

foreach var of varlist p132 p166 p167 p221 p224 p237{
	replace `var' = . if `var' ==99999
}

rename p166 total_alumnos

gen tazas_sanitarias_alum = p34/total_alumnos
gen lavamanos_alum = p38/total_alumnos
gen bebederos_por_alum = p40/total_alumnos

rename p42 total_aulas

rename p132 capacidad_alumnos
rename p157 padres_pago_maestros

gen porc_ocupacion = total_alumnos/p167
rename p169 aulas_usadas 
rename p178 total_banyos


gen muebles_reparacion = p221+ p224 + p236
gen muebles_falta = p232

rename p231 escritorio_maestro
rename p268 hay_internet 

rename p277 compu_sirven
rename p292 num_consejo_escolar

gen padres_consejo = p294/num_consejo_escolar
gen maestros_consejo = p295/num_consejo_escolar


//Materiales de la propiedad
rename p13a fenceMaterial 
replace fenceMaterial = . if fenceMaterial > 4
replace fenceMaterial = 0.9 if fenceMaterial ==1
replace fenceMaterial = 0.5 if fenceMaterial ==2
replace fenceMaterial = 0.4 if fenceMaterial ==3
replace fenceMaterial = 0.3 if fenceMaterial ==4

rename p14 wallMaterial 
replace  wallMaterial = . if wallMaterial > 6
replace  wallMaterial = 0.9 if  wallMaterial ==1
replace  wallMaterial = 0.5 if  wallMaterial ==2
replace  wallMaterial = 0.4 if wallMaterial ==3
replace  wallMaterial = 0.3 if  wallMaterial ==4
replace  wallMaterial = 0.2 if  wallMaterial ==5
replace  wallMaterial = 0.1 if  wallMaterial ==6

rename p15 roofMaterial 
replace  roofMaterial = . if roofMaterial > 6
replace  roofMaterial = 0.9 if  roofMaterial ==1
replace  roofMaterial= 0.5 if  roofMaterial ==2
replace  roofMaterial = 0.4 if roofMaterial ==3
replace  roofMaterial = 0.3 if  roofMaterial ==4
replace  roofMaterial = 0.2 if  roofMaterial==5
replace  roofMaterial = 0.1 if roofMaterial ==6

rename p16 floorMaterial 
replace  floorMaterial = . if floorMaterial > 3
replace  floorMaterial = 0.9 if  floorMaterial ==1
replace  floorMaterial= 0.5 if  floorMaterial ==2
replace  floorMaterial = 0.2 if floorMaterial ==3

gen material_propiedad = fenceMaterial +wallMaterial +roofMaterial +floorMaterial 
drop floorMaterial roofMaterial wallMaterial fenceMaterial 

gen compu_por_alumnos = p276/ total_alumnos
gen alumnos_salon = total_aulas/total_alumnos
gen oficinas_por_alum = (p48+p49)/total_alumnos

rename p22 tiene_drenaje
gen calidad_salones = (p52+p62+p72+p82+p92)/5
gen proyectores_alum = p237/total_alumnos
gen compu_de_gob = (p285+p284)/p276
gen banyos_danyados = (p28+p29+p30+p31+p32+p33)/total_alum

drop p1*
drop p2*
drop p3*
drop p4* 
drop p5*
drop p6*
drop p7*
drop p8* 
drop p9* 

save "$basesA\cemabe_general_sum.dta", replace	


//===========================================
//===========================================
//  ENLACE (Calificaciones)
//===========================================
//===========================================

// Le damos formato a todos los años y nos quedamos con los datos de primaria.
//2006
use "$source\ENLACEBASICA\ENLACE2006.dta", clear
replace grado=grado+6 if nivel=="SECUNDARIA" 
drop if  nivel=="SECUNDARIA" 
keep nofolio grado p_esp p_mat cct turno
gen anyo=2006
save "$basesA\B06_fol.dta", replace

//2007
use "$source\ENLACEBASICA\enl07_A.dta", clear
append using  "$source\ENLACEBASICA\enl07_B.dta"
replace grado=grado+6 if nivel=="SECUNDARIA" 
drop if  nivel=="SECUNDARIA" 
rename cal_esp p_esp
rename cal_mat p_mat
keep nofolio grado p_esp p_mat cct turno
gen anyo=2007
save "$basesA\B07_fol.dta", replace

//2008
use "$source\ENLACEBASICA\RESULT_ALUMNOS_08_A.dta", clear
append using  "$source\ENLACEBASICA\enl08_B.dta", force
replace grado=grado+6 if nivel=="SECUNDARIA" 
drop if  nivel=="SECUNDARIA" 
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_c_n p_ciencias
keep nofolio copia grado p_esp p_mat p_ciencias cct turno
gen anyo=2008
save "$basesA\B08_fol.dta", replace

//2009
use "$source\ENLACEBASICA\RESULT_ALUMNOS_09_A.dta", clear
append using  "$source\ENLACEBASICA\RESULT_ALUMNOS_09_B.dta", force
cap destring grado, replace
replace grado=grado+6 if nivel=="SECUNDARIA" 
drop if  nivel=="SECUNDARIA" 
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_fce p_fce
keep nofolio copia grado p_fce p_esp p_mat cct  turno
gen anyo=2000+9
save "$basesA\B09_fol.dta", replace

//2010
import delimited "$source\2010Mauricio\basica\RES_ENLACE_10_2.csv", clear
replace grado=grado+6 if nivel=="SECUNDARIA" 
drop if  nivel=="SECUNDARIA" 
* nos deshacemos de los curp que tienen más de una observación
bysort nofolio: drop if _N>1
*reemplazamos los valores faltantes 
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_new p_historia
keep nofolio grado copia  p_historia p_esp p_mat cct turno
gen anyo=2010
save "$basesA\B10_fol.dta", replace


//2011
import delimited "$source\2011\resul_enlace_11.csv", varn(1) clear
save "$source\2011\resul_enlace_11.dta", replace
import delimited "$source\2011\alumnos_curp_11.csv", varn(1) clear
save "$source\2011\alumnos_curp_11.dta", replace

use "$source\2011\resul_enlace_11.dta", clear
drop if  nivel=="SECUNDARIA" 
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_new p_geografia
keep nofolio grado copia p_esp p_geografia p_mat cct  turno
gen anyo=2011
save "$basesA\B11_fol.dta", replace
					   
//2012                
use "$source\ENLACEBASICA\resul_alum_eb12.dta", clear
drop if  nivel=="SECUNDARIA" 
rename NOFOLIO nofolio
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_cie p_ciencias
keep nofolio copia grado p_esp p_mat p_ciencias cct  turno
gen anyo=2012
save "$basesA\B12_fol.dta", replace

//2013                 
use "$source\enl2013_alum.dta", clear
rename cal_esp p_esp
rename cal_mat p_mat
rename cal_fce p_fce
destring turno, replace force
destring grado, replace force
gen anyo=2013
replace grado=grado+6 if nivel=="SECUNDARIA"
drop if  nivel=="SECUNDARIA" 
keep nofolio copia grado anyo  p_esp p_mat p_fce cct turno
save "$basesA\B13_fol.dta", replace

//Crea panel de calificaciones
use "$basesA\B08_fol.dta", clear
foreach anyo1 in  09 10 11 12 13  {
	append using "$basesA\\B`anyo1'_r.dta", force
}
save "$basesA\gran_panel.dta", replace


//Limpia y  estandariza por año
//08 09 10 11 12 13
foreach anyo1 in 07 {
	use "$basesA\B`anyo1'_fol.dta", clear
	merge m:1 cct turno using "$basesD\escuelas_tipo.dta"
	keep if _merge == 3
	drop _merge
	foreach tipoE in 1 2 3{
		preserve
			keep if tipo == `tipoE'
			replace copia = "1" if copia == "*"
			destring copia, replace force
			bysort cct turno grado: egen num_copia = count(copia)
			bysort cct turno grado: egen num_stud = count(nofolio)
			gen perc_copia = num_copia/num_stud

			drop if perc_copia >.8
			drop if copia==1

			drop if p_mat == 0  
			drop if missing(p_mat)
			
			bysort grado: egen Q3 = pctile(p_mat), p(75)
			bysort grado: egen Q1 = pctile(p_mat), p(25)
			gen IQR = Q3 - Q1
			
			gen lower = Q1 - 1.5*IQR
			gen upper = Q3 + 1.5*IQR
			
			di `upper'
			drop if p_mat > upper
				di `lower'
			drop if p_mat < lower

			collapse p_mat, by(cct turno grado)

			foreach vari in medmat sdmat p_mat_std{
			cap drop `vari'
			}
			bysort grado: egen medmat=mean(p_mat)
			bysort grado: egen sdmat=sd(p_mat)

			gen p_mat_std=(p_mat-medmat)/sdmat
			drop medmat sdmat
			
			collapse  p_mat_std , by(cct turno)
			gen anyo = 2000 + `anyo1'
			destring turno, replace force
			
			gsort  -p_mat_std
			gen percentile = _n /_N
			gen quintil =1
			replace quintil = 2 if percentile> 0.20 & !missing(percentile)
			replace quintil = 3 if percentile> 0.40 & !missing(percentile)
			replace quintil = 4 if percentile> 0.60 & !missing(percentile)
			replace quintil = 5 if percentile> 0.80 & !missing(percentile)
			rename quintil quintil_`anyo1'
			rename percentile percentile_`anyo1'
			rename p_mat_std p_mat_std_`anyo1'
			
			save "$basesA\B`anyo1'_ef_`tipoE'.dta", replace
		restore
	}
}


//=======================================================================
//=======================================================================
//  F 9 1 1 
//=======================================================================
//=======================================================================
//Lee bases
//Inicio
foreach i in 7 8 { 
	local j = `i'+ 1
	foreach letra in C G I{
		import dbase using "$f911\BD_911_200`i'-200`j'\Inicio\PRIM`letra'I0`i'.DBF", clear
		save "$basesD\I_`letra'_`j'.dta", replace	
	}
}
foreach letra in C G I{
	local i = 9
	local j = `i'+ 1
	import dbase using "$f911\BD_911_200`i'-20`j'\Inicio\PRIM`letra'NAL.DBF", clear
	save "$basesD\I_`letra'_`j'.dta", replace	
}
foreach i in 10 11 12 { 
	local j = `i'+ 1
	foreach letra in C G I{
		import dbase using "$f911\BD_911_20`i'-20`j'\Inicio\PRIM`letra'I`i'.DBF", clear
		save "$basesD\I_`letra'_`j'.dta", replace	
	}
}	
//Fin
foreach i in 7 8 { 
	local j = `i'+ 1
	foreach letra in C G I{
		import dbase using "$f911\BD_911_200`i'-200`j'\Fin\PRIM`letra'F0`i'.DBF", clear
		save "$basesD\F_`letra'_`j'.dta", replace	
	}
}
foreach letra in C G I{
	local i = 9
	local j = `i'+ 1
	import dbase using "$f911\BD_911_200`i'-20`j'\Fin\PRIM`letra'F0`i'.DBF", clear
	save "$basesD\F_`letra'_`j'.dta", replace	
}
foreach i in 10 11 12 { 
	local j = `i'+ 1
	foreach letra in C G I{
		import dbase using "$f911\BD_911_20`i'-20`j'\Fin\PRIM`letra'F`i'.DBF", clear
		save "$basesD\F_`letra'_`j'.dta", replace	
	}
}

// Genera bases de inicio a fin
foreach letra in C G I{
	foreach j in 8 9 10 11 12 13{
		use  "$basesD\F_`letra'_`j'.dta", clear
		foreach var of varlist V*{
			rename `var' `var'_F
		}
		merge 1:1 CLAVECCT TURNO using "$basesD\I_`letra'_`j'.dta"
		drop _merge
		gen cct = substr(CLAVECCT, 1, 10)
		rename TURNO turno
		destring turno, replace force
		save "$basesD\IF_`letra'_`j'.dta", replace
	}
}
	
//=======================================================================
// Ingenieria de Características F911
//=======================================================================

foreach i in 8 9 10 11 12 13{
	use  "$basesD\IF_G_`i'.dta",clear
	gen anyo = 2000 + `i'
	
	// =========================== Final =========================== 
	foreach var of varlist VAR597 VAR609 VAR621 VAR561 VAR573 VAR585 VAR525 VAR537 VAR549{
		replace `var' = . if `var'==0
	} 
	gen tot_inscripcion = VAR597
	gen tot_existencia = VAR609
	gen porc_tot_existencia = VAR609/VAR597
	gen porc_tot_aprobados = VAR621/VAR609
	
	gen m_inscripcion = VAR561/tot_inscripcion
	gen porc_m_existencia = VAR573/VAR561
	gen porc_m_aprobados = VAR585/VAR573
	
	gen h_inscripcion = VAR525/tot_inscripcion
	gen porc_h_existencia = VAR537/VAR525
	gen porc_h_aprobados = VAR549/VAR537
	
	gen prop_mh_aprobados = porc_m_aprobados/porc_h_aprobados
	gen prop_mh_inscripcion = m_inscripcion/h_inscripcion
	gen prop_mh_final = VAR585/VAR549
	
	gen prop_extranjeros_final = VAR646/tot_existencia
	gen prop_indigenas_final = VAR649/tot_existencia
	gen prop_discapacidad_final = VAR652/tot_existencia
	gen prop_sobresaliente_final = VAR655/tot_existencia
	gen prop_usaer_final = VAR658/tot_existencia
	
	replace VAR665 = . if VAR665==0
	gen alums_grupo_tot_final = tot_existencia/VAR665
	gen alums_grupo_sexto_final = VAR506/VAR664
	gen alums_grupo_quinto_final = VAR442/VAR663
	gen alums_grupo_cuarto_final = VAR369/VAR662
	gen alums_grupo_tercero_final = VAR287/VAR661
	
	replace VAR673 = . if VAR673==0
	gen alums_maestro_final = tot_existencia/VAR676
	
	replace VAR682 = . if VAR682==0
	gen alums_personal_final = tot_existencia/VAR682
	gen maestros_final = VAR676
	gen prop_directivo_grupo_final = VAR674/(VAR674+VAR675)
	gen admin_final = VAR681
	
	//=========================== Inicial =========================== 
	gen alums_inicial = V347
	gen prop_repetidores = (V335+V312)/alums_inicial 
	
	gen prop_mh_inicial = (V324+V335)/(V301+V312)
	gen prop_extranjeros_inicial = V399/alums_inicial
	gen prop_indigenas_inicial = V372/alums_inicial
	gen prop_discapacidad_inicial = V429/alums_inicial
	gen prop_sobresaliente_inicial = V423/alums_inicial
	gen prop_usaer_inicial = V402/alums_inicial
	
	gen alums_grupo_tot_inicial = alums_inicial/V348
	gen alums_grupo_sexto_inicial = V288/V289
	gen alums_grupo_quinto_inicial =V252/V253
	gen alums_grupo_cuarto_inicial = V211/V212
	gen alums_grupo_tercero_inicial = V165/V166

	gen alums_maestro_inicial = alums_inicial/(V824 + V825)
	gen alums_personal_inicial = alums_inicial/(V836)
	gen maestros_inicial = (V824 + V825)
	gen prop_directivo_grupo_inicial = (V820+V821)/((V820+V821)+(V822+V823))
	gen admin_inicial = V836
	
	// =========================== Cambio =========================== 
	gen cambio_matricula = (alums_inicial - tot_existencia)/alums_inicial
	gen cambio_prop_mh = (prop_mh_final - prop_mh_inicial)
	gen cambio_alums_grupo = alums_grupo_tot_final - alums_grupo_tot_inicial
	gen cambio_alums_maestro = alums_maestro_final - alums_maestro_inicial
	gen cambio_alums_personal =alums_personal_final - alums_personal_inicial
	gen cambio_maestros = maestros_final - maestros_inicial
	gen cambio_admin = admin_final - admin_inicial
	
	//=========================== Otras inicial ==================================
	//Tercero de primaria
	gen suma = 0
	local edad = 7
	foreach var of varlist V156-V164{
		gen prim_`edad' = `var'*`edad'
		local edad = `edad'+1
	}
	foreach var of varlist prim_7-prim_15{
		replace suma =suma+`var'
	}
	drop prim_*
	gen prom_edad_3 = suma/V165
	drop suma

	//Cu_arteo de primaria
	gen suma = 0
	local edad = 8
	foreach var of varlist V203-V210{
		gen prim_`edad' = `var'*`edad'
		local edad = `edad'+1
	}
	local edad = 8
	foreach var of varlist prim_`edad'-prim_15{
		replace suma =suma+`var'
	}
	drop prim_*
	gen prom_edad_4 = suma/V211
	drop suma

	//Quinto de primaria
	gen suma = 0
	local edad = 9
	foreach var of varlist V245-V251{
		gen prim_`edad' = `var'*`edad'
		local edad = `edad'+1
	}
	local edad = 9
	foreach var of varlist prim_`edad'-prim_15{
		replace suma =suma+`var'
	}
	drop prim_*
	gen prom_edad_5 = suma/V252
	drop suma

	//Sexto de primaria
	gen suma = 0
	local edad = 10
	foreach var of varlist V282-V287{
		gen prim_`edad' = `var'*`edad'
		local edad = `edad'+1
	}
	local edad = 10
	foreach var of varlist prim_`edad'-prim_15{
		replace suma =suma+`var'
	}
	drop prim_*
	gen prom_edad_6 = suma/V288
	drop suma

	//Edad primaria
	gen suma = 0
	local edad = 5
	foreach var of varlist V336-V346{
		gen prim_`edad' = `var'*`edad'
		local edad = `edad'+1
	}
	local edad = 5
	foreach var of varlist prim_`edad'-prim_15{
		replace suma =suma+`var'
	}
	drop prim_*
	rename V347 totum
	gen prom_edad_prim = suma/totum
	drop suma

	//preescolar attendance (1 year or more)
	rename V58 alum1
	gen cursa_preescolar = V369/alum1

	gen tot_m =(V324+V335)
	gen tot_h =(V301+V312)
	
	//escolaridad promedio de preescolar
	gen prom_preescolar_anyos = ((V351+V354)+2*(V357+V360)+3*(V363+V366))/alum1
	gen prom_preescolar_anyos_m = ((V350+V353)+2*(V356+V359)+3*(V362+V365))/ (V35 + V46)
	gen prom_preescolar_anyos_h = ((V349+V352)+2*(V355+V358)+3*(V361+V364))/ (V12 + V23)

	//indigenas_ alum
	gen indigenas_alum = V372/totum
	gen indigenas_alum_m = V371 /tot_m
	gen indigenas_alum_h = V370 /tot_h

	//extranjeros_ alum
	gen extranjeros_alum = V399/totum
	gen extranjeros_alum_m = V398 /tot_m
	gen extranjeros_alum_h = V397 /tot_h

	gen extranjeros_alum_usa = V375/totum
	gen extranjeros_alum_canada = V378/totum
	gen extranjeros_alum_centralA = V381/totum
	gen extranjeros_alum_southA = V384/totum
	gen extranjeros_alum_africa = V387/totum
	gen extranjeros_alum_asia = V390/totum
	gen extranjeros_alum_euro = V393/totum
	gen extranjeros_alum_oceania = V396/totum


	//USAER alum
	gen usaer_alum = V402/totum
	gen usaer_alum_m = V401 /tot_m
	gen usaer_alum_h = V400 /tot_h


	//sudents with discap_
	gen discap_alum = V429/totum
	gen discap_alum_m = V428 /tot_m
	gen discap_alum_h = V427 /tot_h

	gen discap_alum_blindness = V405/totum
	gen discap_alum_vision = V408/totum
	gen discap_alum_deaf = V411/totum
	gen discap_alum_hearing = V414/totum
	gen discap_alum_mobility = V417/totum
	gen discap_alum_intelectual = V420/totum
	gen discap_alum_genius = V423/totum

	
	gen alum_especiales= V432/totum
	gen alum_especiales_m = V431 /tot_m
	gen alum_especiales_h = V430 /tot_h

	//alum_ maestro _prop (alum / _EFrsonal docente)
	gen tot_maestros=(V824+V825)
	gen alum_maestro_prop = totum / tot_maestros
	gen mh_prop_maestros = V824/V825
	gen normal_maestros = ((V549+V550)+ (V581+V581)+ (V613+V614)+(V565+V566)+ ///
	(V597+V598)+ (V629+V630)+ (V645+V646))/ tot_maestros
	// Primaria incompleta = 3, secundaria incompleta = 7,maestria incompleta=17
	//  profesional tecnico 12, pasante =titulado
	gen prom_esc_anyos_maestros = (3*(V437+V438) + 6*(V453+V454) ///
	+ 7*(V469+V470) + 9*(V485+V486) + 10*(V517+V518) +12*(V533+V534) ///
	+12*(V501+V502) + 14*( (V549+V550) + (V581+V581)+ (V613+V614))  ///
	+16*((V565+V566)+(V597+V598)+ (V629+V630)+ (V645+V646))  ///
	+14*(V661+V662)+16*((V677+V678)+(V693+V694)) ///
	+17*(V709+V710)+18*(V725+V726)+19*(V741+V742) + 22*(V757+V758))/tot_maestros

	gen prop_maestros_titulados =  ((V565+V566)+(V597+V598)+ (V629+V630)+ ///
	(V645+V646)+(V677+V678)+(V693+V694)+(V709+V710)+(V725+V726)+(V741+V742) +(V757+V758))/ tot_maestros

	//Personal directivo con grupo 
	gen directores_maestros = (V820+V821)/((V820+V821)+(V822+V823))
	gen mh_prop_directores=(V820+V822)/(V821+V823)

	gen mh_prop_EF=V826/V827
	gen mh_prop_arte=V828/V829
	gen mh_prop_tecno=V830/V831
	gen mh_prop_idioma =V832/V833

	rename V836 tot_personal
	gen maestros_especiales=((V826+V827)+(V828+V829)+(V830+V831)+(V832+V833))/tot_personal
	gen admin_personal = (V834+V835)/tot_personal


	gen alum_personal_prop = totum /tot_personal
	gen alum_maestro__EF =  totum /(V826+V827)
	gen alum_maestro__arte =  totum /(V828+V829)
	gen alum_maestro__tecno =  totum /(V830+V831)
	gen alum_maestro__idioma =  totum /(V832+V833)

	//horas que trabaja profesr
	rename V872 horas_EF
	rename V873 horas_arte
	rename V874 horas_tecno
	rename V875 horas_idioma

	//Carrerea Magisterial
	gen prop_carr_magisterial = V876/tot_personal
	gen nivelCarrMagis_1V =(1*V877+2*V878+3*V879+4*V880+5*V881+6*V882)/tot_maestros
	gen nivelCarrMagis =(1*(V877+V883+V889)+2*(V878+V884+V890)+ ///  
	3*(V879+V885+V891)+4*(V880+V886+V892)+5*(V881+V887+V893)+6*(V882+V888+V894))/V876

	//Aulas 
	gen salon_en_uso  = V903/V895
	gen alum_salon=totum/V903
	gen salones_adaptados =V911/V903

	//Costo
	gen costo_esc= V912+V913+V914
	gen colegiatura = V915+V916*V917+V920*V921
	gen costo_transporte = V920*V921
	//===========================================================
	drop V*
	if `i' <10{
		save "$basesD\G_0`i'.dta", replace
	}
	else{
		save "$basesD\G_`i'.dta", replace
	}
	
}


//Genera variables de cambio con variables generadas
//CON VARIABLES
foreach ant in 08 09 10 11 {
	local anyo1 = `ant' + 1
	use "$basesD\G_`ant'.dta", clear
	foreach var of varlist alum1-costo_transporte{
		rename `var' a_`var'
	}	
	rename a_cct cct
	merge 1:1 cct turno using "$basesD\G_`anyo1'.dta"
	keep if _merge == 3
	drop _merge
	//Generar variables de cambio
	foreach var of varlist alum1-costo_transporte{
		gen dif_`var' = `var' - a_`var'
		gen p_`var' = `var' / a_`var'
	}
	
	save "$basesA\cambio_a_`anyo1'_`ant'_2.dta", replace
	
}


foreach anyo1 in 09 10 11 12 {
		if `anyo1' == 09{
			local ant = "08"
		}
		else if `anyo1' == 10{
			local ant = "09"
		}
		else{
			local ant = `anyo1' - 1
		}
		local sig = `anyo1' + 1
		use "$basesA\B`ant'_ef_2.dta", clear
		merge 1:1 cct turno using "$basesA\B`anyo1'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_std = p_mat_std_`anyo1'- p_mat_std_`ant'
		drop if missing(cambio_std)
		gen pendiente = 0
		replace pendiente = (cambio_std < 0 & !missing(cambio_std))
		merge 1:1 cct turno using "$basesA\B`sig'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_final = p_mat_std_`sig'-p_mat_std_`anyo1'
		drop if missing(cambio_final)
		gen semaforo_std = 0
		replace semaforo_std = (cambio_final< -0.2 & !missing(cambio_final))
		drop p_mat_std_`sig' percentile_`sig' quintil_`sig' cambio_final anyo
		rename p_mat_std_`ant' p_mat_std_ant
		rename p_mat_std_`anyo1' p_mat_std_actual
		rename quintil_`ant' quintil_ant
		rename quintil_`anyo1' quintil_actual
		rename percentile_`ant' percentile_ant
		rename percentile_`anyo1' percentile_actual

		merge m:1 cct using  "$basesA\escuelas_enlace_info.dta"
		drop if _merge == 2
		drop _merge
		replace margina = 0 if missing(margina)
		gen edo = substr(cct, 1,2)
		gen sost = substr(cct, 3,1)
		gen estatal = (sost=="E")
		gen federal = (sost=="D")
		gen priv = (sost=="P")
		destring edo, replace force
		drop sost

		merge 1:1 cct turno using "$basesA\cambio_a_`anyo1'_`ant'_2.dta"
		keep if _merge ==3
		drop _merge 
		drop N_ENTIDAD-DISPON CLAVECCT N_CLAVECCT
		drop if missing(semaforo_std)
		
		merge 1:1 cct turno using "$basesA\cemabe_general_sum.dta"
		keep if _merge ==3
		drop _merge
		drop ageb
		
		compress
		save "$basesA\set_`anyo1'_`ant'.dta", replace
		//export delimited  "$basesA\set_`anyo1'_`ant'.csv", replace
}

use "$basesA\set_09_08.dta", clear
foreach anyo1 in 10 11 {
		if `anyo1' == 10{
			local ant = "09"
		}
		else{
			local ant = `anyo1' - 1
		}
		append using "$basesA\set_`anyo1'_`ant'.dta"
}

save "$basesA\slidding_train_1.dta", replace
export delimited  "$basesA\slide_train_1.csv", replace	
		
use "$basesA\set_12_11.dta", replace
export delimited  "$basesA\slide_test_1.csv", replace

/// VENTANA 2
foreach anyo1 in 09 10 11 {
		if `anyo1' == 09{
			local ant = "08"
		}
		else if `anyo1' == 10{
			local ant = "09"
		}
		else{
			local ant = `anyo1' - 1
		}
		local sig = `anyo1' + 2
		use "$basesA\B`ant'_ef_2.dta", clear
		merge 1:1 cct turno using "$basesA\B`anyo1'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_std = p_mat_std_`anyo1'- p_mat_std_`ant'
		drop if missing(cambio_std)
		gen pendiente = 0
		replace pendiente = (cambio_std < 0 & !missing(cambio_std))
		merge 1:1 cct turno using "$basesA\B`sig'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_final = p_mat_std_`sig'-p_mat_std_`anyo1'
		drop if missing(cambio_final)
		gen semaforo_std = 0
		replace semaforo_std = (cambio_final< -0.2 & !missing(cambio_final))
		drop p_mat_std_`sig' percentile_`sig' quintil_`sig' cambio_final anyo
		rename p_mat_std_`ant' p_mat_std_ant
		rename p_mat_std_`anyo1' p_mat_std_actual
		rename quintil_`ant' quintil_ant
		rename quintil_`anyo1' quintil_actual
		rename percentile_`ant' percentile_ant
		rename percentile_`anyo1' percentile_actual

		merge m:1 cct using  "$basesA\escuelas_enlace_info.dta"
		drop if _merge == 2
		drop _merge
		replace margina = 0 if missing(margina)
		gen edo = substr(cct, 1,2)
		gen sost = substr(cct, 3,1)
		gen estatal = (sost=="E")
		gen federal = (sost=="D")
		gen priv = (sost=="P")
		destring edo, replace force
		drop sost

		merge 1:1 cct turno using "$basesA\cambio_a_`anyo1'_`ant'_2.dta"
		keep if _merge ==3
		drop _merge 
		drop N_ENTIDAD-DISPON CLAVECCT N_CLAVECCT
		drop if missing(semaforo_std)
		compress
		save "$basesA\set_`anyo1'_`ant'_S2.dta", replace
		//export delimited  "$basesA\set_`anyo1'_`ant'.csv", replace
}

use "$basesA\set_09_08_S2.dta", clear
foreach anyo1 in 10 {
		if `anyo1' == 10{
			local ant = "09"
		}
		else{
			local ant = `anyo1' - 1
		}
		append using "$basesA\set_`anyo1'_`ant'_S2.dta"
}

save "$basesA\slidding_train_2.dta", replace
export delimited  "$basesA\slide_train_2.csv", replace	
		
use "$basesA\set_11_10_S2.dta", replace
export delimited  "$basesA\slide_test_2.csv", replace



/// VENTANA 3
foreach anyo1 in 09 10 {
		if `anyo1' == 09{
			local ant = "08"
		}
		else if `anyo1' == 10{
			local ant = "09"
		}
		else{
			local ant = `anyo1' - 1
		}
		local sig = `anyo1' + 3
		use "$basesA\B`ant'_ef_2.dta", clear
		merge 1:1 cct turno using "$basesA\B`anyo1'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_std = p_mat_std_`anyo1'- p_mat_std_`ant'
		drop if missing(cambio_std)
		gen pendiente = 0
		replace pendiente = (cambio_std < 0 & !missing(cambio_std))
		merge 1:1 cct turno using "$basesA\B`sig'_ef_2.dta"
		keep if _merge ==3
		drop _merge
		gen cambio_final = p_mat_std_`sig'-p_mat_std_`anyo1'
		drop if missing(cambio_final)
		gen semaforo_std = 0
		replace semaforo_std = (cambio_final< -0.2 & !missing(cambio_final))
		drop p_mat_std_`sig' percentile_`sig' quintil_`sig' cambio_final anyo
		rename p_mat_std_`ant' p_mat_std_ant
		rename p_mat_std_`anyo1' p_mat_std_actual
		rename quintil_`ant' quintil_ant
		rename quintil_`anyo1' quintil_actual
		rename percentile_`ant' percentile_ant
		rename percentile_`anyo1' percentile_actual

		merge m:1 cct using  "$basesA\escuelas_enlace_info.dta"
		drop if _merge == 2
		drop _merge
		replace margina = 0 if missing(margina)
		gen edo = substr(cct, 1,2)
		gen sost = substr(cct, 3,1)
		gen estatal = (sost=="E")
		gen federal = (sost=="D")
		gen priv = (sost=="P")
		destring edo, replace force
		drop sost

		merge 1:1 cct turno using "$basesA\cambio_a_`anyo1'_`ant'_2.dta"
		keep if _merge ==3
		drop _merge 
		drop N_ENTIDAD-DISPON CLAVECCT N_CLAVECCT
		drop if missing(semaforo_std)
		compress
		save "$basesA\set_`anyo1'_`ant'_S3.dta", replace
		//export delimited  "$basesA\set_`anyo1'_`ant'.csv", replace
}

use "$basesA\set_09_08_S3.dta", clear
save "$basesA\slidding_train_3.dta", replace
export delimited  "$basesA\slide_train_3.csv", replace	
		
use "$basesA\set_10_09_S3.dta", replace
export delimited  "$basesA\slide_test_3.csv", replace


from airflow.hooks.base import BaseHook
from airflow.models import Variable
from coopdevsutils import dataframetotable, executequery, querytodataframe


def loadanswers(campaign):
    conndwh = BaseHook.get_connection('DWH').get_hook().get_sqlalchemy_engine()

    if campaign is None:
        where = " and year>=(date_part('year', current_date)-1)::varchar "
    else:
        where = f" and year='{campaign}' "


    qry =f"""
        drop table if exists external.full_answers;
        create table external.full_answers as
        with recursive method_section_hieriarchy as (
            select distinct s.id
                , s.title
                , coalesce(s.title_en, s.title) as title_en
                , coalesce(s.title_ca, s.title) as title_ca
                , coalesce(s.title_gl, s.title) as title_gl
                , coalesce(s.title_eu, s.title) as title_eu
                , coalesce(s.title_es, s.title) as title_es
                , coalesce(s.title_nl, s.title) as title_nl
                , coalesce(s.title_fr, s.title) as title_fr
                , s.order, s.method_id, s.parent_id, 1 as lvl, cast(s.order as text) as path_order
            from syh_methods_section s
            where parent_id is null
            union all
            select distinct s.id
                , s.title
                , coalesce(s.title_en, s.title) as title_en
                , coalesce(s.title_ca, s.title) as title_ca
                , coalesce(s.title_gl, s.title) as title_gl
                , coalesce(s.title_eu, s.title) as title_eu
                , coalesce(s.title_es, s.title) as title_es
                , coalesce(s.title_nl, s.title) as title_nl
                , coalesce(s.title_fr, s.title) as title_fr
                , s.order, s.method_id, s.parent_id, ms.lvl+1 as lvl, ms.path_order || '.' || lpad(s.order::varchar,2,'0') AS path_order
            from syh_methods_section s
                join method_section_hieriarchy ms on ms.id=s.parent_id
            )
        select 
            c.id as id_campaign
            ,  c.name as campaign_name
            ,  coalesce(c.name_en, c.name) as campaign_name_en
            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
            ,  coalesce(c.name_es, c.name) as campaign_name_es
            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
            , c.year, c.previous_campaign_id
            , m.id as id_method
            , m.name as method_name
            ,  coalesce(m.name_en, m.name) as method_name_en
            ,  coalesce(m.name_ca, m.name) as method_name_ca
            ,  coalesce(m.name_gl, m.name) as method_name_gl
            ,  coalesce(m.name_eu, m.name) as method_name_eu
            ,  coalesce(m.name_es, m.name) as method_name_es
            ,  coalesce(m.name_nl, m.name) as method_name_nl
            ,  coalesce(m.name_fr, m.name) as method_name_fr
            , m.description as method_description
            ,  coalesce(m.description_en, m.description) as method_description_en
            ,  coalesce(m.description_ca, m.description) as method_description_ca
            ,  coalesce(m.description_gl, m.description) as method_description_gl
            ,  coalesce(m.description_eu, m.description) as method_description_eu
            ,  coalesce(m.description_es, m.description) as method_description_es
            ,  coalesce(m.description_nl, m.description) as method_description_nl
            ,  coalesce(m.description_fr, m.description) as method_description_fr
            , null::uuid as id_methods_section
            , 'Indirect indicator'::varchar(500) as method_section_title
            , 'Indirect indicator'::varchar(500) as method_section_title_en
            , 'Indicator indirecte'::varchar(500) as method_section_title_ca
            , 'Indirect indicator'::varchar(500) as method_section_title_gl
            , 'Indirect indicator'::varchar(500) as method_section_title_eu
            , 'Indicador indirecto'::varchar(500) as method_section_title_es
            , 'Indirect indicator'::varchar(500) as method_section_title_nl
            , 'Indirect indicator'::varchar(500) as method_section_title_fr
            , 999 as method_order,1 as method_level, '9999.01' as path_order
            , 999 as sort_value
            , i.id as id_indicator, i.code as indicator_code
            , i.name as indicator_name
            , coalesce(i.name_en, i.name) as indicator_name_en
            , coalesce(i.name_ca, i.name) as indicator_name_ca
            , coalesce(i.name_gl, i.name) as indicator_name_gl
            , coalesce(i.name_eu, i.name) as indicator_name_eu
            , coalesce(i.name_es, i.name) as indicator_name_es
            , coalesce(i.name_nl, i.name) as indicator_name_nl
            , coalesce(i.name_fr, i.name) as indicator_name_fr
            , i.description as indicator_description
            , coalesce(i.description_en, i.description) as indicator_description_en
            , coalesce(i.description_ca, i.description) as indicator_description_ca
            , coalesce(i.description_gl, i.description) as indicator_description_gl
            , coalesce(i.description_eu, i.description) as indicator_description_eu
            , coalesce(i.description_es, i.description) as indicator_description_es
            , coalesce(i.description_nl, i.description) as indicator_description_nl
            , coalesce(i.description_fr, i.description) as indicator_description_fr
            , i.is_direct_indicator, i.category as indicator_category, i.data_type as indicator_data_type, i.unit as indicator_unit
            , sml.id as list_item_id
            , replace(sml.title,'"','″') as list_item_title
            , replace(coalesce(sml.title_en, sml.title),'"','″') as list_item_title_en
            , replace(coalesce(sml.title_ca, sml.title),'"','″') as list_item_title_ca
            , replace(coalesce(sml.title_gl, sml.title),'"','″') as list_item_title_gl
            , replace(coalesce(sml.title_eu, sml.title),'"','″') as list_item_title_eu
            , replace(coalesce(sml.title_es, sml.title),'"','″') as list_item_title_es
            , replace(coalesce(sml.title_nl, sml.title),'"','″') as list_item_title_nl
            , replace(coalesce(sml.title_fr, sml.title),'"','″') as list_item_title_fr
            , g1.id as g1_id
            , replace(g1.title,'"','″') as g1_title
            , replace(coalesce(g1.title_en, g1.title),'"','″') as g1_title_en
            , replace(coalesce(g1.title_ca, g1.title),'"','″') as g1_title_ca
            , replace(coalesce(g1.title_gl, g1.title),'"','″') as g1_title_gl
            , replace(coalesce(g1.title_eu, g1.title),'"','″') as g1_title_eu
            , replace(coalesce(g1.title_es, g1.title),'"','″') as g1_title_es
            , replace(coalesce(g1.title_nl, g1.title),'"','″') as g1_title_nl
            , replace(coalesce(g1.title_fr, g1.title),'"','″') as g1_title_fr
            , g2.id as g2_id
            , replace(g2.title,'"','″') as g2_title
            , replace(coalesce(g2.title_en, g2.title),'"','″') as g2_title_en
            , replace(coalesce(g2.title_ca, g2.title),'"','″') as g2_title_ca
            , replace(coalesce(g2.title_gl, g2.title),'"','″') as g2_title_gl
            , replace(coalesce(g2.title_eu, g2.title),'"','″') as g2_title_eu
            , replace(coalesce(g2.title_es, g2.title),'"','″') as g2_title_es
            , replace(coalesce(g2.title_nl, g2.title),'"','″') as g2_title_nl
            , replace(coalesce(g2.title_fr, g2.title),'"','″') as g2_title_fr
        from 
            syh_methods_campaign c 
            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
            join syh_methods_method m on mcm.method_id = m.id 
            join syh_methods_method_indicators mi on m.id = mi.method_id
            join syh_methods_indicator i on mi.indicator_id = i.id 
            left join syh_methods_list l on i.list_options_id = l.id and i.data_type in ('CH', 'R', 'DR')
            left join syh_methods_list_items li on l.id = li.list_id 
            left join syh_methods_listitem sml on li.listitem_id = sml.id 
            left join syh_methods_group_items gi on gi.group_id = i.group_id 
            left join syh_methods_groupitem g1 on gi.groupitem_id  = g1.id 
            left join syh_methods_group mg on gi.group_id = mg.id 
            left join syh_methods_group_items gi2 on gi2.group_id = i.group_2_id  
            left join syh_methods_groupitem g2 on gi2.groupitem_id  = g2.id 
            left join syh_methods_group mg2 on gi2.group_id = mg2.id 
        where 1=1 
            {where}
        union all
        
                -- TOTALS grup 2
        select distinct
	            c.id as id_campaign
	            ,  c.name as campaign_name
	            ,  coalesce(c.name_en, c.name) as campaign_name_en
	            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
	            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
	            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
	            ,  coalesce(c.name_es, c.name) as campaign_name_es
	            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
	            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
	            , c.year, c.previous_campaign_id
	            , m.id as id_method
	            , m.name as method_name
	            ,  coalesce(m.name_en, m.name) as method_name_en
	            ,  coalesce(m.name_ca, m.name) as method_name_ca
	            ,  coalesce(m.name_gl, m.name) as method_name_gl
	            ,  coalesce(m.name_eu, m.name) as method_name_eu
	            ,  coalesce(m.name_es, m.name) as method_name_es
	            ,  coalesce(m.name_nl, m.name) as method_name_nl
	            ,  coalesce(m.name_fr, m.name) as method_name_fr
	            , m.description as method_description
	            ,  coalesce(m.description_en, m.description) as method_description_en
	            ,  coalesce(m.description_ca, m.description) as method_description_ca
	            ,  coalesce(m.description_gl, m.description) as method_description_gl
	            ,  coalesce(m.description_eu, m.description) as method_description_eu
	            ,  coalesce(m.description_es, m.description) as method_description_es
	            ,  coalesce(m.description_nl, m.description) as method_description_nl
	            ,  coalesce(m.description_fr, m.description) as method_description_fr
	            , null::uuid as id_methods_section
	            , 'Indirect indicator'::varchar(500) as method_section_title
	            , 'Indirect indicator'::varchar(500) as method_section_title_en
	            , 'Indicator indirecte'::varchar(500) as method_section_title_ca
	            , 'Indirect indicator'::varchar(500) as method_section_title_gl
	            , 'Indirect indicator'::varchar(500) as method_section_title_eu
	            , 'Indicador indirecto'::varchar(500) as method_section_title_es
	            , 'Indirect indicator'::varchar(500) as method_section_title_nl
	            , 'Indirect indicator'::varchar(500) as method_section_title_fr
	            , 999 as method_order,1 as method_level, '9999.01' as path_order
	            , 999 as sort_value
	            , i.id as id_indicator, i.code as indicator_code
	            , i.name as indicator_name
	            , coalesce(i.name_en, i.name) as indicator_name_en
	            , coalesce(i.name_ca, i.name) as indicator_name_ca
	            , coalesce(i.name_gl, i.name) as indicator_name_gl
	            , coalesce(i.name_eu, i.name) as indicator_name_eu
	            , coalesce(i.name_es, i.name) as indicator_name_es
	            , coalesce(i.name_nl, i.name) as indicator_name_nl
	            , coalesce(i.name_fr, i.name) as indicator_name_fr
	            , i.description as indicator_description
	            , coalesce(i.description_en, i.description) as indicator_description_en
	            , coalesce(i.description_ca, i.description) as indicator_description_ca
	            , coalesce(i.description_gl, i.description) as indicator_description_gl
	            , coalesce(i.description_eu, i.description) as indicator_description_eu
	            , coalesce(i.description_es, i.description) as indicator_description_es
	            , coalesce(i.description_nl, i.description) as indicator_description_nl
	            , coalesce(i.description_fr, i.description) as indicator_description_fr
	            , i.is_direct_indicator, i.category as indicator_category, i.data_type as indicator_data_type, i.unit as indicator_unit
	            , sml.id as list_item_id
	            , replace(sml.title,'"','″') as list_item_title
	            , replace(coalesce(sml.title_en, sml.title),'"','″') as list_item_title_en
	            , replace(coalesce(sml.title_ca, sml.title),'"','″') as list_item_title_ca
	            , replace(coalesce(sml.title_gl, sml.title),'"','″') as list_item_title_gl
	            , replace(coalesce(sml.title_eu, sml.title),'"','″') as list_item_title_eu
	            , replace(coalesce(sml.title_es, sml.title),'"','″') as list_item_title_es
	            , replace(coalesce(sml.title_nl, sml.title),'"','″') as list_item_title_nl
	            , replace(coalesce(sml.title_fr, sml.title),'"','″') as list_item_title_fr
	            , null::uuid as g1_id
	            , 'TOTAL' as g1_title
	            , 'TOTAL' as g1_title_en
	            , 'TOTAL' as g1_title_ca
	            , 'TOTAL' as g1_title_gl
	            , 'TOTAL' as g1_title_eu
	            , 'TOTAL' as g1_title_es
	            , 'TOTAL' as g1_title_nl
	            , 'TOTAL' as g1_title_fr
	            , g2.id as g2_id
	            , replace(g2.title,'"','″') as g2_title
	            , replace(coalesce(g2.title_en, g2.title),'"','″') as g2_title_en
	            , replace(coalesce(g2.title_ca, g2.title),'"','″') as g2_title_ca
	            , replace(coalesce(g2.title_gl, g2.title),'"','″') as g2_title_gl
	            , replace(coalesce(g2.title_eu, g2.title),'"','″') as g2_title_eu
	            , replace(coalesce(g2.title_es, g2.title),'"','″') as g2_title_es
	            , replace(coalesce(g2.title_nl, g2.title),'"','″') as g2_title_nl
	            , replace(coalesce(g2.title_fr, g2.title),'"','″') as g2_title_fr
	        from 
	            syh_methods_campaign c 
	            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
	            join syh_methods_method m on mcm.method_id = m.id 
	            join syh_methods_method_indicators mi on m.id = mi.method_id
	            join syh_methods_indicator i on mi.indicator_id = i.id 
	            left join syh_methods_list l on i.list_options_id = l.id and i.data_type in ('CH', 'R', 'DR')
	            left join syh_methods_list_items li on l.id = li.list_id 
	            left join syh_methods_listitem sml on li.listitem_id = sml.id 
	            left join syh_methods_group_items gi on gi.group_id = i.group_id 
	            left join syh_methods_groupitem g1 on gi.groupitem_id  = g1.id 
	            left join syh_methods_group mg on gi.group_id = mg.id 
	            left join syh_methods_group_items gi2 on gi2.group_id = i.group_2_id  
	            left join syh_methods_groupitem g2 on gi2.groupitem_id  = g2.id 
	            left join syh_methods_group mg2 on gi2.group_id = mg2.id 
	        where 1=1 
	        and group_2_total
            {where}
        union all
        -- TOTALS grup 1
         select distinct
            c.id as id_campaign
            ,  c.name as campaign_name
            ,  coalesce(c.name_en, c.name) as campaign_name_en
            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
            ,  coalesce(c.name_es, c.name) as campaign_name_es
            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
            , c.year, c.previous_campaign_id
            , m.id as id_method
            , m.name as method_name
            ,  coalesce(m.name_en, m.name) as method_name_en
            ,  coalesce(m.name_ca, m.name) as method_name_ca
            ,  coalesce(m.name_gl, m.name) as method_name_gl
            ,  coalesce(m.name_eu, m.name) as method_name_eu
            ,  coalesce(m.name_es, m.name) as method_name_es
            ,  coalesce(m.name_nl, m.name) as method_name_nl
            ,  coalesce(m.name_fr, m.name) as method_name_fr
            , m.description as method_description
            ,  coalesce(m.description_en, m.description) as method_description_en
            ,  coalesce(m.description_ca, m.description) as method_description_ca
            ,  coalesce(m.description_gl, m.description) as method_description_gl
            ,  coalesce(m.description_eu, m.description) as method_description_eu
            ,  coalesce(m.description_es, m.description) as method_description_es
            ,  coalesce(m.description_nl, m.description) as method_description_nl
            ,  coalesce(m.description_fr, m.description) as method_description_fr
            , null::uuid as id_methods_section
            , 'Indirect indicator'::varchar(500) as method_section_title
            , 'Indirect indicator'::varchar(500) as method_section_title_en
            , 'Indicator indirecte'::varchar(500) as method_section_title_ca
            , 'Indirect indicator'::varchar(500) as method_section_title_gl
            , 'Indirect indicator'::varchar(500) as method_section_title_eu
            , 'Indicador indirecto'::varchar(500) as method_section_title_es
            , 'Indirect indicator'::varchar(500) as method_section_title_nl
            , 'Indirect indicator'::varchar(500) as method_section_title_fr
            , 999 as method_order,1 as method_level, '9999.01' as path_order
            , 999 as sort_value
            , i.id as id_indicator, i.code as indicator_code
            , i.name as indicator_name
            , coalesce(i.name_en, i.name) as indicator_name_en
            , coalesce(i.name_ca, i.name) as indicator_name_ca
            , coalesce(i.name_gl, i.name) as indicator_name_gl
            , coalesce(i.name_eu, i.name) as indicator_name_eu
            , coalesce(i.name_es, i.name) as indicator_name_es
            , coalesce(i.name_nl, i.name) as indicator_name_nl
            , coalesce(i.name_fr, i.name) as indicator_name_fr
            , i.description as indicator_description
            , coalesce(i.description_en, i.description) as indicator_description_en
            , coalesce(i.description_ca, i.description) as indicator_description_ca
            , coalesce(i.description_gl, i.description) as indicator_description_gl
            , coalesce(i.description_eu, i.description) as indicator_description_eu
            , coalesce(i.description_es, i.description) as indicator_description_es
            , coalesce(i.description_nl, i.description) as indicator_description_nl
            , coalesce(i.description_fr, i.description) as indicator_description_fr
            , i.is_direct_indicator, i.category as indicator_category, i.data_type as indicator_data_type, i.unit as indicator_unit
            , sml.id as list_item_id
            , replace(sml.title,'"','″') as list_item_title
            , replace(coalesce(sml.title_en, sml.title),'"','″') as list_item_title_en
            , replace(coalesce(sml.title_ca, sml.title),'"','″') as list_item_title_ca
            , replace(coalesce(sml.title_gl, sml.title),'"','″') as list_item_title_gl
            , replace(coalesce(sml.title_eu, sml.title),'"','″') as list_item_title_eu
            , replace(coalesce(sml.title_es, sml.title),'"','″') as list_item_title_es
            , replace(coalesce(sml.title_nl, sml.title),'"','″') as list_item_title_nl
            , replace(coalesce(sml.title_fr, sml.title),'"','″') as list_item_title_fr
            , g1.id as g1_id
            , replace(g1.title,'"','″') as g1_title
            , replace(coalesce(g1.title_en, g1.title),'"','″') as g1_title_en
            , replace(coalesce(g1.title_ca, g1.title),'"','″') as g1_title_ca
            , replace(coalesce(g1.title_gl, g1.title),'"','″') as g1_title_gl
            , replace(coalesce(g1.title_eu, g1.title),'"','″') as g1_title_eu
            , replace(coalesce(g1.title_es, g1.title),'"','″') as g1_title_es
            , replace(coalesce(g1.title_nl, g1.title),'"','″') as g1_title_nl
            , replace(coalesce(g1.title_fr, g1.title),'"','″') as g1_title_fr
             , null::uuid as g2_id
            , 'TOTAL' as g2_title
            , 'TOTAL'  as g2_title_en
            , 'TOTAL'  as g2_title_ca
            , 'TOTAL'  as g2_title_gl
            , 'TOTAL'  as g2_title_eu
            , 'TOTAL'  as g2_title_es
            , 'TOTAL'  as g2_title_nl
            , 'TOTAL'  as g2_title_fr
        from 
            syh_methods_campaign c 
            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
            join syh_methods_method m on mcm.method_id = m.id 
            join syh_methods_method_indicators mi on m.id = mi.method_id
            join syh_methods_indicator i on mi.indicator_id = i.id 
            left join syh_methods_list l on i.list_options_id = l.id and i.data_type in ('CH', 'R', 'DR')
            left join syh_methods_list_items li on l.id = li.list_id 
            left join syh_methods_listitem sml on li.listitem_id = sml.id 
            left join syh_methods_group_items gi on gi.group_id = i.group_id 
            left join syh_methods_groupitem g1 on gi.groupitem_id  = g1.id 
            left join syh_methods_group mg on gi.group_id = mg.id 
            left join syh_methods_group_items gi2 on gi2.group_id = i.group_2_id  
            left join syh_methods_groupitem g2 on gi2.groupitem_id  = g2.id 
            left join syh_methods_group mg2 on gi2.group_id = mg2.id 
        where 1=1 
        and group_total
        {where}
        -- TOTALS grup 1 i grup 2
        union all
        select distinct
            c.id as id_campaign
            ,  c.name as campaign_name
            ,  coalesce(c.name_en, c.name) as campaign_name_en
            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
            ,  coalesce(c.name_es, c.name) as campaign_name_es
            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
            , c.year, c.previous_campaign_id
            , m.id as id_method
            , m.name as method_name
            ,  coalesce(m.name_en, m.name) as method_name_en
            ,  coalesce(m.name_ca, m.name) as method_name_ca
            ,  coalesce(m.name_gl, m.name) as method_name_gl
            ,  coalesce(m.name_eu, m.name) as method_name_eu
            ,  coalesce(m.name_es, m.name) as method_name_es
            ,  coalesce(m.name_nl, m.name) as method_name_nl
            ,  coalesce(m.name_fr, m.name) as method_name_fr
            , m.description as method_description
            ,  coalesce(m.description_en, m.description) as method_description_en
            ,  coalesce(m.description_ca, m.description) as method_description_ca
            ,  coalesce(m.description_gl, m.description) as method_description_gl
            ,  coalesce(m.description_eu, m.description) as method_description_eu
            ,  coalesce(m.description_es, m.description) as method_description_es
            ,  coalesce(m.description_nl, m.description) as method_description_nl
            ,  coalesce(m.description_fr, m.description) as method_description_fr
            , null::uuid as id_methods_section
            , 'Indirect indicator'::varchar(500) as method_section_title
            , 'Indirect indicator'::varchar(500) as method_section_title_en
            , 'Indicator indirecte'::varchar(500) as method_section_title_ca
            , 'Indirect indicator'::varchar(500) as method_section_title_gl
            , 'Indirect indicator'::varchar(500) as method_section_title_eu
            , 'Indicador indirecto'::varchar(500) as method_section_title_es
            , 'Indirect indicator'::varchar(500) as method_section_title_nl
            , 'Indirect indicator'::varchar(500) as method_section_title_fr
            , 999 as method_order,1 as method_level, '9999.01' as path_order
            , 999 as sort_value
            , i.id as id_indicator, i.code as indicator_code
            , i.name as indicator_name
            , coalesce(i.name_en, i.name) as indicator_name_en
            , coalesce(i.name_ca, i.name) as indicator_name_ca
            , coalesce(i.name_gl, i.name) as indicator_name_gl
            , coalesce(i.name_eu, i.name) as indicator_name_eu
            , coalesce(i.name_es, i.name) as indicator_name_es
            , coalesce(i.name_nl, i.name) as indicator_name_nl
            , coalesce(i.name_fr, i.name) as indicator_name_fr
            , i.description as indicator_description
            , coalesce(i.description_en, i.description) as indicator_description_en
            , coalesce(i.description_ca, i.description) as indicator_description_ca
            , coalesce(i.description_gl, i.description) as indicator_description_gl
            , coalesce(i.description_eu, i.description) as indicator_description_eu
            , coalesce(i.description_es, i.description) as indicator_description_es
            , coalesce(i.description_nl, i.description) as indicator_description_nl
            , coalesce(i.description_fr, i.description) as indicator_description_fr
            , i.is_direct_indicator, i.category as indicator_category, i.data_type as indicator_data_type, i.unit as indicator_unit
            , sml.id as list_item_id
            , replace(sml.title,'"','″') as list_item_title
            , replace(coalesce(sml.title_en, sml.title),'"','″') as list_item_title_en
            , replace(coalesce(sml.title_ca, sml.title),'"','″') as list_item_title_ca
            , replace(coalesce(sml.title_gl, sml.title),'"','″') as list_item_title_gl
            , replace(coalesce(sml.title_eu, sml.title),'"','″') as list_item_title_eu
            , replace(coalesce(sml.title_es, sml.title),'"','″') as list_item_title_es
            , replace(coalesce(sml.title_nl, sml.title),'"','″') as list_item_title_nl
            , replace(coalesce(sml.title_fr, sml.title),'"','″') as list_item_title_fr
            , null::uuid as g1_id
            , 'TOTAL' as g1_title
            , 'TOTAL' as g1_title_en
            , 'TOTAL' as g1_title_ca
            , 'TOTAL' as g1_title_gl
            , 'TOTAL' as g1_title_eu
            , 'TOTAL' as g1_title_es
            , 'TOTAL' as g1_title_nl
            , 'TOTAL' as g1_title_fr
             , null::uuid as g2_id
            , 'TOTAL' as g2_title
            , 'TOTAL'  as g2_title_en
            , 'TOTAL'  as g2_title_ca
            , 'TOTAL'  as g2_title_gl
            , 'TOTAL'  as g2_title_eu
            , 'TOTAL'  as g2_title_es
            , 'TOTAL'  as g2_title_nl
            , 'TOTAL'  as g2_title_fr
        from 
            syh_methods_campaign c 
            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
            join syh_methods_method m on mcm.method_id = m.id 
            join syh_methods_method_indicators mi on m.id = mi.method_id
            join syh_methods_indicator i on mi.indicator_id = i.id 
            left join syh_methods_list l on i.list_options_id = l.id and i.data_type in ('CH', 'R', 'DR')
            left join syh_methods_list_items li on l.id = li.list_id 
            left join syh_methods_listitem sml on li.listitem_id = sml.id 
            left join syh_methods_group_items gi on gi.group_id = i.group_id 
            left join syh_methods_groupitem g1 on gi.groupitem_id  = g1.id 
            left join syh_methods_group mg on gi.group_id = mg.id 
            left join syh_methods_group_items gi2 on gi2.group_id = i.group_2_id  
            left join syh_methods_groupitem g2 on gi2.groupitem_id  = g2.id 
            left join syh_methods_group mg2 on gi2.group_id = mg2.id 
        where 1=1 
        and group_total
        and group_2_total
        {where}
        
        union all
        select 
            c.id as id_campaign
            ,  c.name as campaign_name
            ,  coalesce(c.name_en, c.name) as campaign_name_en
            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
            ,  coalesce(c.name_es, c.name) as campaign_name_es
            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
            , c.year, c.previous_campaign_id
            , m.id as id_method
            , m.name as method_name
            ,  coalesce(m.name_en, m.name) as method_name_en
            ,  coalesce(m.name_ca, m.name) as method_name_ca
            ,  coalesce(m.name_gl, m.name) as method_name_gl
            ,  coalesce(m.name_eu, m.name) as method_name_eu
            ,  coalesce(m.name_es, m.name) as method_name_es
            ,  coalesce(m.name_nl, m.name) as method_name_nl
            ,  coalesce(m.name_fr, m.name) as method_name_fr
            , m.description as method_description
            ,  coalesce(m.description_en, m.description) as method_description_en
            ,  coalesce(m.description_ca, m.description) as method_description_ca
            ,  coalesce(m.description_gl, m.description) as method_description_gl
            ,  coalesce(m.description_eu, m.description) as method_description_eu
            ,  coalesce(m.description_es, m.description) as method_description_es
            ,  coalesce(m.description_nl, m.description) as method_description_nl
            ,  coalesce(m.description_fr, m.description) as method_description_fr
            , h.id as id_methods_section
            , h.title as method_section_title
            , coalesce(h.title_en, h.title) as method_section_title_en
            , coalesce(h.title_ca, h.title) as method_section_title_ca
            , coalesce(h.title_gl, h.title) as method_section_title_gl
            , coalesce(h.title_eu, h.title) as method_section_title_eu
            , coalesce(h.title_es, h.title) as method_section_title_es
            , coalesce(h.title_nl, h.title) as method_section_title_nl
            , coalesce(h.title_fr, h.title) as method_section_title_fr
            , h.order as method_order, h.lvl as method_level, h.path_order
            , si.sort_value
            , null::uuid as id_indicator, null as indicator_code
            , null as indicator_name
            , null as indicator_name_en, null as indicator_name_ca, null as indicator_name_gl
            , null as indicator_name_eu, null as indicator_name_es, null as indicator_name_nl
            , null as indicator_name_fr
            , null as indicator_description
            , null as indicator_description_en, null as indicator_description_ca
            , null as indicator_description_gl, null as indicator_description_eu
            , null as indicator_description_es, null as indicator_description_nl
            , null as indicator_description_fr
            , false as is_direct_indicator, null as indicator_category, null as indicator_data_type, null as indicator_unit
            , null::uuid as list_item_id
            , null::varchar as list_item_title
            , null::varchar as list_item_title_en
            , null::varchar as list_item_title_ca
            , null::varchar as list_item_title_gl
            , null::varchar as list_item_title_eu
            , null::varchar as list_item_title_es
            , null::varchar as list_item_title_nl
            , null::varchar as list_item_title_fr
            , null::uuid as g1_id
            , null::varchar as g1_title
            , null::varchar as g1_title_en
            , null::varchar as g1_title_ca
            , null::varchar as g1_title_gl
            , null::varchar as g1_title_eu
            , null::varchar as g1_title_es
            , null::varchar as g1_title_nl
            , null::varchar as g1_title_fr
            , null::uuid as g2_id
            , null::varchar as g2_title
            , null::varchar as g2_title_en
            , null::varchar as g2_title_ca
            , null::varchar as g2_title_gl
            , null::varchar as g2_title_eu
            , null::varchar as g2_title_es
            , null::varchar as g2_title_nl
            , null::varchar as g2_title_fr
        from 
            syh_methods_campaign c 
            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
            join syh_methods_method m on mcm.method_id = m.id 
            join method_section_hieriarchy h on h.method_id=m.id
            left join syh_methods_section_indicators si on si.section_id=h.id
        where 1=1 
            {where}
        union all
        select 
            c.id as id_campaign
            ,  c.name as campaign_name
            ,  coalesce(c.name_en, c.name) as campaign_name_en
            ,  coalesce(c.name_ca, c.name) as campaign_name_ca
            ,  coalesce(c.name_gl, c.name) as campaign_name_gl
            ,  coalesce(c.name_eu, c.name) as campaign_name_eu
            ,  coalesce(c.name_es, c.name) as campaign_name_es
            ,  coalesce(c.name_nl, c.name) as campaign_name_nl
            ,  coalesce(c.name_fr, c.name) as campaign_name_fr
            , c.year, c.previous_campaign_id
            , m.id as id_method
            , m.name as method_name
            ,  coalesce(m.name_en, m.name) as method_name_en
            ,  coalesce(m.name_ca, m.name) as method_name_ca
            ,  coalesce(m.name_gl, m.name) as method_name_gl
            ,  coalesce(m.name_eu, m.name) as method_name_eu
            ,  coalesce(m.name_es, m.name) as method_name_es
            ,  coalesce(m.name_nl, m.name) as method_name_nl
            ,  coalesce(m.name_fr, m.name) as method_name_fr
            , m.description as method_description
            ,  coalesce(m.description_en, m.description) as method_description_en
            ,  coalesce(m.description_ca, m.description) as method_description_ca
            ,  coalesce(m.description_gl, m.description) as method_description_gl
            ,  coalesce(m.description_eu, m.description) as method_description_eu
            ,  coalesce(m.description_es, m.description) as method_description_es
            ,  coalesce(m.description_nl, m.description) as method_description_nl
            ,  coalesce(m.description_fr, m.description) as method_description_fr
            , h.id as id_methods_section
            , h.title as method_section_title
            , coalesce(h.title_en, h.title) as method_section_title_en
            , coalesce(h.title_ca, h.title) as method_section_title_ca
            , coalesce(h.title_gl, h.title) as method_section_title_gl
            , coalesce(h.title_eu, h.title) as method_section_title_eu
            , coalesce(h.title_es, h.title) as method_section_title_es
            , coalesce(h.title_nl, h.title) as method_section_title_nl
            , coalesce(h.title_fr, h.title) as method_section_title_fr
            , h.order as method_order, h.lvl as method_level, h.path_order
            , si.sort_value
            , null::uuid as id_indicator, null as indicator_code
            , null as indicator_name
            , null as indicator_name_en, null as indicator_name_ca, null as indicator_name_gl
            , null as indicator_name_eu, null as indicator_name_es, null as indicator_name_nl
            , null as indicator_name_fr
            , null as indicator_description
            , null as indicator_description_en, null as indicator_description_ca
            , null as indicator_description_gl, null as indicator_description_eu
            , null as indicator_description_es, null as indicator_description_nl
            , null as indicator_description_fr
            , true as is_direct_indicator, null as indicator_category, null as indicator_data_type, null as indicator_unit
            , null::uuid as list_item_id
            , null::varchar as list_item_title
            , null::varchar as list_item_title_en
            , null::varchar as list_item_title_ca
            , null::varchar as list_item_title_gl
            , null::varchar as list_item_title_eu
            , null::varchar as list_item_title_es
            , null::varchar as list_item_title_nl
            , null::varchar as list_item_title_fr
            , null::uuid as g1_id
            , null::varchar as g1_title
            , null::varchar as g1_title_en
            , null::varchar as g1_title_ca
            , null::varchar as g1_title_gl
            , null::varchar as g1_title_eu
            , null::varchar as g1_title_es
            , null::varchar as g1_title_nl
            , null::varchar as g1_title_fr
            , null::uuid as g2_id
            , null::varchar as g2_title
            , null::varchar as g2_title_en
            , null::varchar as g2_title_ca
            , null::varchar as g2_title_gl
            , null::varchar as g2_title_eu
            , null::varchar as g2_title_es
            , null::varchar as g2_title_nl
            , null::varchar as g2_title_fr
        from 
            syh_methods_campaign c 
            join syh_methods_campaign_methods mcm on mcm.campaign_id = c.id 
            join syh_methods_method m on mcm.method_id = m.id 
            join method_section_hieriarchy h on h.method_id=m.id
            left join syh_methods_section_indicators si on si.section_id=h.id
            where 1=1 
            {where}
        ;
        
        commit;
    """
    executequery(qry, conndwh)
    print("FI full_answers")

    qry = f"""
        drop table if exists external.method_section_hieriarchy;
        create table external.method_section_hieriarchy as
        with recursive method_section_hieriarchy as (
        select distinct s.id
            , s.title, s.title_en, s.title_ca, s.title_gl, s.title_eu, s.title_es, s.title_nl, s.title_fr
            , s.order, s.method_id, s.parent_id, 1 as lvl, cast(s.order as text) as path_order
        from syh_methods_section s
        where parent_id is null
        union all
        select distinct s.id
            , s.title, s.title_en, s.title_ca, s.title_gl, s.title_eu, s.title_es, s.title_nl, s.title_fr
            , s.order, s.method_id, s.parent_id, ms.lvl+1 as lvl, ms.path_order || '.' || lpad(s.order::varchar,2,'0') AS path_order
        from syh_methods_section s
            join method_section_hieriarchy ms on ms.id=s.parent_id
        )
        select *
        from method_section_hieriarchy;
        
        drop table if exists external.syh_methods_section_indicators;
        create table external.syh_methods_section_indicators as
        select*
        from syh_methods_section_indicators;
        
        update external.full_answers  set id_methods_section=h.id
                , method_section_title=h.title
                , method_section_title_en=coalesce(h.title_en,h.title)
                , method_section_title_ca=coalesce(h.title_ca,h.title)
                , method_section_title_gl=coalesce(h.title_gl,h.title)
                , method_section_title_eu=coalesce(h.title_eu,h.title)
                , method_section_title_es=coalesce(h.title_es,h.title)
                , method_section_title_nl=coalesce(h.title_nl,h.title)
                , method_section_title_fr=coalesce(h.title_fr,h.title)
                , method_order=h."order"
                , method_level=h.lvl
                , path_order=h.path_order
                , sort_value=si.sort_value
        from external.method_section_hieriarchy h
        join external.syh_methods_section_indicators si on si.section_id=h.id
        where full_answers.id_indicator=si.indicator_id and full_answers.id_method=h.method_id
            and id_methods_section is null;
    
        commit;
    """
    executequery(qry, conndwh)
    print("FI update full_answers")

    qry = f"""
        
        drop table if exists external.organization_project;
        create table external.organization_project as
        select u.id as id_user, u.name as user_name, u.surnames as user_surname, u.email as user_email
                , o.id as id_organization, o.name as organization_name, o.vat_number --TODO afegir més camps
                , pr.id as id_project, pr.name as project_name
                , s.campaign_id, s.method_id, s.id as id_survey, s.status, s.created_at as survey_created_at, s.updated_at as survey_updated_at
        from syh_methods_survey s
        left join syh_organizations_project pr on s.project_id=pr.id
                join syh_organizations_organization o on s.organization_id=o.id
                join syh_users_user u on s.user_id=u.id
                join syh_methods_campaign c on s.campaign_id=c.id
        where 1=1
        {where};
         
          
        create index cix_op on  external.organization_project  (campaign_id, method_id) ;     
        CLUSTER external.organization_project USING cix_op;
        

        create index cix_fa on external.full_answers  (id_campaign, id_method);
        CLUSTER external.full_answers USING cix_fa;
            
        commit;
    """
    executequery(qry, conndwh)
    print("FI organization_project")

    qry = f"""
            drop table if exists external.full_answers_organization_project;

            create table external.full_answers_organization_project as
            select   s.*     
            ,  f.*
            from external.organization_project s
            join external.full_answers f on s.campaign_id = f.id_campaign and s.method_id = f.id_method;
    
            commit;
        """
    executequery(qry, conndwh)
    print("FI full_answers_organization_project")

    qry = f"""
            drop table if exists external.full_answers_organization_project_subconjunt;
            create table external.full_answers_organization_project_subconjunt as
            select *
            from external.full_answers_organization_project ac
            where 1=1
                {where}
            ;
             
            commit;   
            """
    executequery(qry, conndwh)
    print("FI full_answers_organization_project_subconjunt")

    qry = f"""
            create index cix_aops on  external.full_answers_organization_project_subconjunt  (id_indicator, id_survey);
            CLUSTER external.full_answers_organization_project_subconjunt USING cix_aops;

            commit;
        """
    executequery(qry, conndwh)
    print("FI cix_aops")

    qry = f"""
            drop table if exists external.methods_indicatorresult_unnest;
            create table external.methods_indicatorresult_unnest as
            select  indicator_id, survey_id, gender, group_item_id, group_2_item_id
            , unnest(string_to_array(value,'|')) as value_unnest
            , instance_number
            from syh_methods_indicatorresult;
            
            create index ci_mir on  external.methods_indicatorresult_unnest  (indicator_id, survey_id);
            CLUSTER external.methods_indicatorresult_unnest USING ci_mir;
            
            commit;
          """
    executequery(qry, conndwh)
    print("FI methods_indicatorresult_unnest")

    qry = f"""
            truncate table external.answers_calc_subconjunt ;
            --delete from external.answers_calc_subconjunt 
            --where 1=1 {where};

            commit;
        """
    executequery(qry, conndwh)
    print("FI delete answers_calc_subconjunt")

    qry = f"""
                
        insert into  external.answers_calc_subconjunt 
        select s.*
            , case when u.value_unnest is not null then '1' else '0'end as value, gender::text
            , u.instance_number
        from  external.full_answers_organization_project_subconjunt s
            left join external.methods_indicatorresult_unnest u
                on s.id_survey=u.survey_id 
                    and s.id_indicator=u.indicator_id 
                    and s.list_item_id::text=u.value_unnest
        where s.list_item_id is not null
        union all
        select s.*
            , value_unnest::text as value, gender::text
            , u.instance_number
        from  external.full_answers_organization_project_subconjunt s
            left join external.methods_indicatorresult_unnest u
                on s.id_survey=u.survey_id 
                    and s.id_indicator=u.indicator_id 
                    and s.g1_id=u.group_item_id
        where s.g1_id is not null
            and s.g2_id is null and u.group_2_item_id is null	
        union all
        select s.*
            , value_unnest::text as value, gender::text
            , u.instance_number
        from  external.full_answers_organization_project_subconjunt s
            left join external.methods_indicatorresult_unnest u
                on s.id_survey=u.survey_id 
                    and s.id_indicator=u.indicator_id 
                    and s.g2_id=u.group_2_item_id
        where s.g1_id is null and u.group_item_id is null
            and s.g2_id is not null    
        union all
        select s.*
            , value_unnest::text as value, gender::text
            , u.instance_number
        from  external.full_answers_organization_project_subconjunt s
            left join external.methods_indicatorresult_unnest u
                on s.id_survey=u.survey_id 
                    and s.id_indicator=u.indicator_id 
                    and s.g1_id=u.group_item_id
                    and s.g2_id=u.group_2_item_id
        where s.g1_id is not null
            and s.g2_id is not null	
        union all	
        select s.*
        , value_unnest::text as value, gender::text
        , u.instance_number
        from  external.full_answers_organization_project_subconjunt s
            left join external.methods_indicatorresult_unnest u
                on s.id_survey=u.survey_id 
                    and s.id_indicator=u.indicator_id 
        where s.g1_id is null and u.group_item_id is null
            and s.g2_id is null and u.group_2_item_id is null	
            and s.list_item_id is null;	


        commit;
        """
    executequery(qry, conndwh)
    print("FI insert answers_calc_subconjunt")

    qry = f"""
            delete from external.answers_calc_agg_full
            where 1=1 
            {where};
            
            
            insert into external.answers_calc_agg_full
            select id_campaign
                , max(campaign_name) as campaign_name
                , max(campaign_name_en) as campaign_name_en
                , max(campaign_name_ca) as campaign_name_ca
                , max(campaign_name_es) as campaign_name_es
                , max(campaign_name_eu) as campaign_name_eu
                , max(campaign_name_gl) as campaign_name_gl
                , max(campaign_name_nl) as campaign_name_nl
                , max(campaign_name_fr) as campaign_name_fr
                , max("year") as "year", max(previous_campaign_id::varchar)::uuid as previous_campaign_id
                , id_survey, max(survey_created_at) as survey_created_at, max(survey_updated_at) as survey_updated_at
                , max(status) as status
                , id_method
                , max(method_name) as method_name
                , max(method_name_en) as method_name_en
                , max(method_name_ca) as method_name_ca
                , max(method_name_es) as method_name_es
                , max(method_name_eu) as method_name_eu
                , max(method_name_gl) as method_name_gl
                , max(method_name_nl) as method_name_nl
                , max(method_name_fr) as method_name_fr
                , max(method_description) as method_description
                , max(method_description_en) as method_description_en
                , max(method_description_ca) as method_description_ca
                , max(method_description_es) as method_description_es
                , max(method_description_eu) as method_description_eu
                , max(method_description_gl) as method_description_gl
                , max(method_description_nl) as method_description_nl
                , max(method_description_fr) as method_description_fr
                , id_user, max(user_name) as user_name, max(user_surname) as user_surname, max(user_email) as user_email
                , id_organization, max(organization_name) as organization_name, max(vat_number) as vat_number
                , id_project, max(project_name) as project_name
                , id_methods_section
                , max(method_section_title) as method_section_title
                , max(method_section_title_en) as method_section_title_en
                , max(method_section_title_ca) as method_section_title_ca
                , max(method_section_title_es) as method_section_title_es
                , max(method_section_title_eu) as method_section_title_eu
                , max(method_section_title_gl) as method_section_title_gl
                , max(method_section_title_nl) as method_section_title_nl
                , max(method_section_title_fr) as method_section_title_fr
                , max(method_order) as method_order, max(method_level) as method_level, max(path_order) as path_order
                , max(sort_value) as sort_value
                , id_indicator, indicator_code
                , max(indicator_name) as indicator_name
                , max(indicator_name_en) as indicator_name_en
                , max(indicator_name_ca) as indicator_name_ca
                , max(indicator_name_es) as indicator_name_es
                , max(indicator_name_eu) as indicator_name_eu
                , max(indicator_name_gl) as indicator_name_gl
                , max(indicator_name_nl) as indicator_name_nl
                , max(indicator_name_fr) as indicator_name_fr
                , max(indicator_description) as indicator_description
                , max(indicator_description_en) as indicator_description_en
                , max(indicator_description_ca) as indicator_description_ca
                , max(indicator_description_es) as indicator_description_es
                , max(indicator_description_eu) as indicator_description_eu
                , max(indicator_description_gl) as indicator_description_gl
                , max(indicator_description_nl) as indicator_description_nl
                , max(indicator_description_fr) as indicator_description_fr
                , is_direct_indicator as is_direct_indicator, max(indicator_category) as indicator_category
                , max(indicator_data_type) as indicator_data_type, max(indicator_unit) as indicator_unit
                , array_agg(
                    case gender when '0' then 'Men'
                        when '1' then 'Women'
                        when '2' then 'Non binary'
                        end
                        ORDER BY gender
                ) as gender
                , array_agg(
                    case gender when '0' then 'Men'
                        when '1' then 'Women'
                        when '2' then 'Non binary'
                        end
                        ORDER BY gender
                ) as gender_en
                , array_agg(
                    case gender when '0' then 'Homes'
                        when '1' then 'Dones'
                        when '2' then 'No binàries'
                        end
                        ORDER BY gender
                ) as gender_ca
                , array_agg(
                    case gender when '0' then 'Hombres'
                        when '1' then 'Mujeres'
                        when '2' then 'No binarias'
                        end
                        ORDER BY gender
                ) as gender_es
                , array_agg(
                    case gender when '0' then 'Gizonak'
                        when '1' then 'Emakumeak'
                        when '2' then 'Ez-binario'
                        end
                        ORDER BY gender
                ) as gender_eu
                , array_agg(
                    case gender when '0' then 'Homes'
                        when '1' then 'Mulleres'
                        when '2' then 'Non binarias'
                        end
                        ORDER BY gender
                ) as gender_gl
                , array_agg(
                    case gender when '0' then 'Hommes'
                        when '1' then 'Femmes'
                        when '2' then 'Non binaires'
                        end
                        ORDER BY gender
                ) as gender_fr
                , array_agg(
                    case gender when '0' then 'Men'
                        when '1' then 'Women'
                        when '2' then 'Non binary'
                        end
                        ORDER BY gender
                ) as gender_nl
                , array_agg(value order by gender) as value
                , count(distinct gender) as num_gender
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Men"'
                        when '1' then '"Women"'
                        when '2' then '"Non binary"'
                        end::varchar,',' order by gender)||']' end as str_gender
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Men"'
                        when '1' then '"Women"'
                        when '2' then '"Non binary"'
                        end::varchar,',' order by gender)||']' end as str_gender_en
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Homes"'
                        when '1' then '"Dones"'
                        when '2' then '"No binàries"'
                        end::varchar,',' order by gender)||']' end as str_gender_ca
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Homes"'
                        when '1' then '"Mujeres"'
                        when '2' then '"No binarias"'
                        end::varchar,',' order by gender)||']' end as str_gender_es
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Gizonak"'
                        when '1' then '"Emakumeak"'
                        when '2' then '"Ez-binario"'
                        end::varchar,',' order by gender)||']' end as str_gender_eu
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Homes"'
                        when '1' then '"Mulleres"'
                        when '2' then '"Non binarias"'
                        end::varchar,',' order by gender)||']' end as str_gender_gl
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Men"'
                        when '1' then '"Women"'
                        when '2' then '"Non binary"'
                        end::varchar,',' order by gender)||']' end as str_gender_nl
                , case when count(distinct gender)>0 then '['||string_agg(case gender when '0' then '"Hommes"'
                        when '1' then '"Femmes"'
                        when '2' then '"Non binaires"'
                        end::varchar,',' order by gender)||']' end as str_gender_fr
                
               , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title,' ◻️ ', g1_title),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title,'","' order by list_item_title)||'"]'
                    end as str_list
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_en,' ◻️ ', g1_title_en),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_en,'","' order by list_item_title)||'"]'
                     end as str_list_en
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_ca,' ◻️ ', g1_title_ca),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title_ca)>0 then '["'||string_agg(list_item_title_ca,'","' order by list_item_title)||'"]'
                     end as str_list_ca
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_es,' ◻️ ', g1_title_es),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_es,'","' order by list_item_title_es)||'"]'
                     end as str_list_es
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_eu,' ◻️ ', g1_title_eu),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_eu,'","' order by list_item_title)||'"]'
                     end as str_list_eu
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_gl,' ◻️ ', g1_title_gl),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_gl,'","' order by list_item_title)||'"]'
                     end as str_list_gl
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_nl,' ◻️ ', g1_title_nl),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_nl,'","' order by list_item_title)||'"]'
                     end as str_list_nl
                , case when count(distinct g2_title)>0 then '["'||string_agg(concat(g2_title_fr,' ◻️ ', g1_title_fr),'","' order by g2_title, g1_title)||'"]'
                    when count(distinct list_item_title)>0 then '["'||string_agg(list_item_title_fr,'","' order by list_item_title)||'"]'
                     end as str_list_fr
   
                    , count(distinct list_item_title)
                , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title, g1_title)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_en, g1_title_en)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_en
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_ca, g1_title_ca)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_ca
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_es, g1_title_es)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                         else string_agg(value,'') end as str_value_es
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_eu, g1_title_eu)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_eu
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_gl, g1_title_gl)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_gl
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_nl, g1_title_nl)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_nl
                    , case when count(distinct gender)>0 then '['||string_agg(value,',' order by gender)||']'
                        when count(distinct g2_title)>0 then '["'||string_agg(value,'","' order by g2_title_fr, g1_title_fr)||'"]'
                        when count(distinct list_item_title)>0 then '['||string_agg(value,',' order by list_item_title)||']'
                        else string_agg(value,'') end as str_value_fr
                    , coalesce(i.code, '') as set_code
                    , ac.instance_number
                    , max(i.sort_value) as set_sort_value
                    , max(i.set_name) as set_name
                    , max(i.set_name_en) as set_name_en
                    , max(i.set_name_ca) as set_name_ca
                    , max(i.set_name_gl) as set_name_gl
                    , max(i.set_name_eu) as set_name_eu
                    , max(i.set_name_es) as set_name_es
                    , max(i.set_name_nl) as set_name_nl
                    , max(i.set_name_fr) as set_name_fr
                    , max(i.set_description) as set_description
                    , max(i.set_description_en) as set_description_en
                    , max(i.set_description_ca) as set_description_ca
                    , max(i.set_description_gl) as set_description_gl
                    , max(i.set_description_eu) as set_description_eu
                    , max(i.set_description_es) as set_description_es
                    , max(i.set_description_nl) as set_description_nl
                    , max(i.set_description_fr) as set_description_fr
                    , max(i.set_instance_name) as set_instance_name
                    , max(i.set_instance_name_en) as set_instance_name_en
                    , max(i.set_instance_name_ca) as set_instance_name_ca
                    , max(i.set_instance_name_gl) as set_instance_name_gl
                    , max(i.set_instance_name_eu) as set_instance_name_eu
                    , max(i.set_instance_name_es) as set_instance_name_es
                    , max(i.set_instance_name_nl) as set_instance_name_nl
                    , max(i.set_instance_name_fr) as set_instance_name_fr
            from external.answers_calc_subconjunt ac
            left join (
                select distinct 
                    i.indicator_id
                    , smi.code
                    , smi.name as set_name
                    , smi.name_en as set_name_en
                    , smi.name_ca as set_name_ca
                    , smi.name_gl as set_name_gl
                    , smi.name_eu as set_name_eu
                    , smi.name_es as set_name_es
                    , smi.name_nl as set_name_nl
                    , smi.name_fr as set_name_fr
                    , smi.description as set_description
                    , smi.description_en as set_description_en
                    , smi.description_ca as set_description_ca
                    , smi.description_gl as set_description_gl
                    , smi.description_eu as set_description_eu
                    , smi.description_es as set_description_es
                    , smi.description_nl as set_description_nl
                    , smi.description_fr as set_description_fr
                    , smi.instance_name as set_instance_name
                    , smi.instance_name_en as set_instance_name_en
                    , smi.instance_name_ca as set_instance_name_ca
                    , smi.instance_name_gl as set_instance_name_gl
                    , smi.instance_name_eu as set_instance_name_eu
                    , smi.instance_name_es as set_instance_name_es
                    , smi.instance_name_nl as set_instance_name_nl
                    , smi.instance_name_fr as set_instance_name_fr
                from syh_methods_indicatorsset_indicators i
                join syh_methods_indicatorsset smi on i.indicatorsset_id=smi.id
            ) i on ac.id_indicator=i.indicator_id
            where 1=1
            {where}
            group by id_campaign,  id_survey, id_method, id_user, id_organization, id_project
                , id_methods_section, id_indicator, indicator_code, is_direct_indicator
                , coalesce(i.code, ''), ac.instance_number
                ;
    
            --create index ci_caf on  external.answers_calc_agg_full  (id_campaign, id_method, id_organization);
            --CLUSTER external.answers_calc_agg_full USING ci_caf;
    
            commit;
        """
    executequery(qry, conndwh)
    print("FI answers_calc_agg_full")

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

import pandas as pd
from repair_records.forms import MassUploadForm
from accounts.models import Factory, Section, User
from repair_records.models import RepairType, Equipment, EquipmentNode, WorkType, WorkAction, RepairRecord


class MassUploadView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/mass_upload.html"
    permission_required = "repair_records.summarize_repairrecord"

    def get(self, request):
        form = MassUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = MassUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data["file"]

            flag = True
            if flag:
                flag = self.messanger(request, "Factory", mass_upload_factory, file)
            if flag:
                flag = self.messanger(request, "Section", mass_upload_section, file)
            if flag:
                flag = self.messanger(
                    request, "Repair Type", mass_upload_repair_type, file
                )
            if flag:
                flag = self.messanger(request, "Work Type", mass_upload_work_type, file)
            if flag:
                flag = self.messanger(
                    request, "Work Action", mass_upload_work_action, file
                )
            if flag:
                flag = self.messanger(request, "Equipment", mass_upload_equipment, file)
            if flag:
                flag = self.messanger(
                    request, "Equipment Node", mass_upload_equipment_node, file
                )

            if flag:
                messages.success(request, _("Mass upload was successful!"))
        else:
            messages.error(request, _("The file is not excel file"))

        return redirect("mass_upload_repair_record")

    def messanger(self, request, name, func, file):
        try:
            func(request, file)
            return True
        except Exception as e:
            print(e)
            messages.error(
                request,
                _(
                    "Could not manage to open sheet %(name)s! \
                Check for correctness of the sheet"
                )
                % {"name": name},
            )
        return False


def mass_upload_factory(request, file):
    # FACTORY
    df_factory = pd.read_excel(file, sheet_name="Factory")
    df_factory = df_factory.where(df_factory.notnull(), None)
    factory_data = df_factory.to_dict(orient="records")

    for i, data in enumerate(factory_data):
        print(data)
        name = data["name"]
        data["equation"] = data["formula"]
        del data["formula"]

        try:
            # Get an existing Factory instance based on name
            factory_instance = Factory.objects.get(name=name)

            # Update existing instance
            for key, value in data.items():
                setattr(factory_instance, key, value)

            factory_instance.save()

        except Factory.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                Factory.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload Factory on row %(row)s: \
                                %(name)s. Check for correctness of data!"
                    )
                    % {
                        "name": name,
                        "row": i + 2,
                    },
                )
        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload Factory on row %(row)s: \
                            %(name)s. Check for correctness of data!"
                )
                % {
                    "name": name,
                    "row": i + 2,
                },
            )


def mass_upload_section(request, file):
    # SECTION
    df_section = pd.read_excel(file, sheet_name="Section")
    df_section = df_section.where(df_section.notnull(), None)
    section_data = df_section.to_dict(orient="records")

    for i, data in enumerate(section_data):
        print(data)
        name = data["name"]
        factory_name = data["factory"]

        try:
            data["factory"] = Factory.objects.get(name=factory_name)
        except Exception as e:
            print(e)

        factory = data["factory"]

        try:
            # Get an existing Section instance based on name and factory
            section_instance = Section.objects.get(name=name, factory=factory)

            # Update existing instance
            for key, value in data.items():
                setattr(section_instance, key, value)

            section_instance.save()

        except Section.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                Section.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload Section on row %(row)s: \
                                %(factory)s - %(name)s. \
                                Check for correctness of data!"
                    )
                    % {
                        "factory": factory_name,
                        "name": name,
                        "row": i + 2,
                    },
                )
        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload Section on row %(row)s: \
                            %(factory)s - %(name)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory_name,
                    "name": name,
                    "row": i + 2,
                },
            )


def mass_upload_repair_type(request, file):
    # REPAIR TYPE
    df_repair_type = pd.read_excel(file, sheet_name="Repair Type")
    df_repair_type = df_repair_type.where(df_repair_type.notnull(), None)
    repair_type_data = df_repair_type.to_dict(orient="records")

    for i, data in enumerate(repair_type_data):
        print(data)

        try:
            data["factory"] = Factory.objects.get(name=data["factory"])
        except Exception as e:
            print(e)

        factory = data["factory"]
        codename = data["codename"]

        try:
            # Get an existing RepairType instance based on factory and codename
            repair_type_instance = RepairType.objects.get(
                factory=factory, codename=codename
            )

            # Update existing instance
            for key, value in data.items():
                setattr(repair_type_instance, key, value)

            repair_type_instance.save()

        except RepairType.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                RepairType.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload RepairType on row %(row)s: \
                                %(factory)s - %(codename)s. \
                                 Check for correctness of data!"
                    )
                    % {
                        "factory": factory.name,
                        "codename": codename,
                        "row": i + 2,
                    },
                )

        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload RepairType on row %(row)s: \
                            %(factory)s - %(codename)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory.name,
                    "codename": codename,
                    "row": i + 2,
                },
            )

def mass_upload_work_type(request, file):
    # WORK TYPE
    df_work_type = pd.read_excel(file, sheet_name="Work Type")
    df_work_type = df_work_type.where(df_work_type.notnull(), None)
    work_type_data = df_work_type.to_dict(orient="records")

    for i, data in enumerate(work_type_data):
        print(data)

        try:
            data["factory"] = Factory.objects.get(name=data["factory"])
        except Exception as e:
            print(e)

        factory = data["factory"]
        name = data["name"]

        try:
            # Get an existing WorkType instance based on factory and name
            work_type_instance = WorkType.objects.get(
                factory=factory, name=name
            )

            # Update existing instance
            for key, value in data.items():
                setattr(work_type_instance, key, value)

            work_type_instance.save()

        except WorkType.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                WorkType.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload WorkType on row %(row)s: \
                                %(factory)s - %(name)s. \
                                 Check for correctness of data!"
                    )
                    % {
                        "factory": factory.name,
                        "name": name,
                        "row": i + 2,
                    },
                )

        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload WorkType on row %(row)s: \
                            %(factory)s - %(name)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory.name,
                    "name": name,
                    "row": i + 2,
                },
            )

def mass_upload_work_action(request, file):
    # WORK ACTION
    df_work_action = pd.read_excel(file, sheet_name="Work Action")
    df_work_action = df_work_action.where(df_work_action.notnull(), None)
    work_action_data = df_work_action.to_dict(orient="records")

    for i, data in enumerate(work_action_data):
        print(data)

        try:
            data["factory"] = Factory.objects.get(name=data["factory"])
        except Exception as e:
            print(e)

        factory = data["factory"]
        name = data["name"]

        try:
            # Get an existing WorkAction instance based on factory and name
            work_action_instance = WorkAction.objects.get(
                factory=factory, name=name
            )

            # Update existing instance
            for key, value in data.items():
                setattr(work_action_instance, key, value)

            work_action_instance.save()

        except WorkAction.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                WorkAction.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload WorkAction on row %(row)s: \
                                %(factory)s - %(name)s. \
                                 Check for correctness of data!"
                    )
                    % {
                        "factory": factory.name,
                        "name": name,
                        "row": i + 2,
                    },
                )

        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload WorkAction on row %(row)s: \
                            %(factory)s - %(name)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory.name,
                    "name": name,
                    "row": i + 2,
                },
            )


def mass_upload_equipment(request, file):
    # EQUIPMENT
    df_equipment = pd.read_excel(file, sheet_name="Equipment")
    df_equipment = df_equipment.where(df_equipment.notnull(), None)
    equipment_data = df_equipment.to_dict(orient="records")

    for i, data in enumerate(equipment_data):
        print(data)
        factory_name = data["factory"]
        section_name = data["section"]
        equipment_codename = data["codename"]
        equipment_name = data["name"]

        try:
            data["section"] = Section.objects.get(
                name=section_name, factory__name=factory_name
            )
        except Exception as e:
            print(e)
        del data["factory"]

        try:
            # Get an existing Equipment instance based on section and factory
            equipment_instance = Equipment.objects.get(
                codename=equipment_codename,
                name=equipment_name,
                section=data["section"],
            )

            # Update existing instance
            for key, value in data.items():
                setattr(equipment_instance, key, value)

            equipment_instance.save()

        except Equipment.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                Equipment.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload Equipment on row %(row)s: \
                                %(factory)s %(section)s - %(equipment)s. \
                                Check for correctness of data!"
                    )
                    % {
                        "factory": factory_name,
                        "section": section_name,
                        "equipment": equipment_codename,
                        "row": i + 2,
                    },
                )
        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload Equipment on row %(row)s: \
                            %(factory)s %(section)s - %(equipment)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory_name,
                    "section": section_name,
                    "equipment": equipment_codename,
                    "row": i + 2,
                },
            )

def mass_upload_equipment_node(request, file):
    # EQUIPMENT NODE
    df_equipment_node = pd.read_excel(file, sheet_name="Equipment Node")
    df_equipment_node = df_equipment_node.where(df_equipment_node.notnull(), None)
    equipment_node_data = df_equipment_node.to_dict(orient="records")

    for i, data in enumerate(equipment_node_data):
        print(data)
        factory_name = data["factory"]
        section_name = data["section"]
        equipment_codename = data["equipment_codename"]
        node_name = data["name"]

        try:
            data["equipment"] = Equipment.objects.get(
                codename=equipment_codename, section__name=section_name, section__factory__name=factory_name
            )
        except Exception as e:
            print(e)
        del data["factory"]
        del data["section"]
        del data["equipment_codename"]

        try:
            # Get an existing EquipmentNode instance based on equipment and section
            equipment_node_instance = EquipmentNode.objects.get(
                name=node_name,
                equipment=data["equipment"],
            )

            # Update existing instance
            for key, value in data.items():
                setattr(equipment_node_instance, key, value)

            equipment_node_instance.save()

        except EquipmentNode.DoesNotExist:
            try:
                # If no existing instance is found, create a new one
                EquipmentNode.objects.create(**data)

            except Exception as e:
                print(e)
                messages.warning(
                    request,
                    _(
                        "Failed to upload Equipment Node on row %(row)s: \
                                %(factory)s %(section)s - %(equipment)s - %(node)s. \
                                Check for correctness of data!"
                    )
                    % {
                        "factory": factory_name,
                        "section": section_name,
                        "equipment": equipment_codename,
                        "node": node_name,
                        "row": i + 2,
                    },
                )
        except Exception as e:
            print(e)
            messages.warning(
                request,
                _(
                    "Failed to upload Equipment Node on row %(row)s: \
                            %(factory)s %(section)s - %(equipment)s - %(node)s. \
                            Check for correctness of data!"
                )
                % {
                    "factory": factory_name,
                    "section": section_name,
                    "equipment": equipment_codename,
                    "node": node_name,
                    "row": i + 2,
                },
            )


'''
USED FOR DATA MIGRATION
def mass_upload_repair_record(request, file):
    # REPAIR RECORD
    df_repair_record = pd.read_excel(file, sheet_name="Repair Record")
    df_repair_record = df_repair_record.where(df_repair_record.notnull(), None)
    repair_record_data = df_repair_record.to_dict(orient="records")

    for i, data in enumerate(repair_record_data):
        factory_id = data['factory']
        section_id = data['section']
        equipment_id = data['equipment']
        repair_type_id = data['repair_type']
        master_id = data['master']
        performers_ids = data['performers']

        print(performers_ids, type(performers_ids))
        if performers_ids and type(performers_ids) != int:
            performers_ids = [int(x) for x in performers_ids.split(" ")]
        elif type(performers_ids) == int:
            performers_ids = [performers_ids]
        del data['performers']

        # get real object ids from models
        data['factory'] = Factory.objects.get(id=factory_id)
        data['section'] = Section.objects.get(id=section_id)
        data['equipment'] = Equipment.objects.get(id=equipment_id)
        data['repair_type'] = RepairType.objects.get(id=repair_type_id)
        data['master'] = User.objects.get(id=master_id)

        if performers_ids:
            performers_ids = User.objects.filter(id__in=performers_ids)

        # convert start_time and end_time from string to datetime
        data['start_time'] = pd.to_datetime(data['start_time'])
        data['end_time'] = pd.to_datetime(data['end_time'])

        # save them
        print(data, performers_ids)
        record = RepairRecord.objects.create(**data)
        if performers_ids:
            record.performers.set(performers_ids)
        record.save()
'''
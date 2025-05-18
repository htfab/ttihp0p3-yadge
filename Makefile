TARGET=gds/tt_um_colorful_stripes.gds

.PHONY: $(TARGET)

$(TARGET): gds/tt_um_template_1x1.gds
	python3 scripts/make_stripes.py

clean:
	rm -f $(TARGET)
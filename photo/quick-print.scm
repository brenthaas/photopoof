(define (quick-print inImage)
  (let* (
         (image (car(gimp-file-load RUN-NONINTERACTIVE inImage inImage)))
         )
    (file-print-gtk RUN-NONINTERACTIVE image)
    (gimp-image-delete image)
  )
)
